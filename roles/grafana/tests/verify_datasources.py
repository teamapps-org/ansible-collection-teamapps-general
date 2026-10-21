"""Local rendering/logging regression check. Requires Ansible and Docker Compose.

Run with the repository's pipenv Python and COMPOSE pointing to a Compose binary.
Only temporary local files are changed; no containers or hosts are started.
"""

import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlencode, urlunsplit
from uuid import uuid4

import yaml


ROLE = Path(__file__).resolve().parents[1]
ROOT = ROLE.parents[1]
COMPOSE = os.environ.get("COMPOSE", "docker")
COMPOSE_CMD = [COMPOSE] + (["compose"] if COMPOSE == "docker" else [])
def synthetic_value(label, suffix=""):
    return label + "_" + uuid4().hex + suffix


SECRET = synthetic_value("DS_CANARY", "_$word_${word}_$$ # quotes ' \" slash \\ newline\nnext\ttab\rreturn ü")


def run(command, **kwargs):
    result = subprocess.run(command, text=True, capture_output=True, **kwargs)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout


with tempfile.TemporaryDirectory(prefix="grafana-datasources-") as directory:
    work = Path(directory)
    role = work / "roles" / "fixture"
    (role / "tasks").mkdir(parents=True)
    (role / "handlers").mkdir()
    (role / "templates").symlink_to(ROLE / "templates")
    (role / "defaults").symlink_to(ROLE / "defaults")
    original = yaml.safe_load((ROLE / "tasks/main.yml").read_text())
    tasks = original[:2] + [task for task in original if task["name"] in {
        "deploy docker-compose.yml", "deploy grafana .env",
        "configure datasource provisioning",
    }]
    for task in tasks:
        for module in ("template", "copy"):
            if module in task:
                task[module].pop("owner", None)
                task[module].pop("group", None)
    (role / "tasks/main.yml").write_text(yaml.safe_dump(tasks))
    (role / "handlers/main.yml").write_text(yaml.safe_dump([
        {"name": "grafana_restart", "debug": {"msg": "local render only"}},
    ]))
    project = work / "project"
    provisioning = project / "provisioning/datasources/default.yml"
    provisioning.parent.mkdir(parents=True)
    collection = work / "collections/ansible_collections/teamapps/general"
    collection.parent.mkdir(parents=True)
    collection.symlink_to(ROOT, target_is_directory=True)
    (work / "ansible.cfg").write_text(
        "[defaults]\nroles_path=roles\n"
        f"collections_path={work / 'collections'}\n"
        "retry_files_enabled=false\n"
    )
    env = os.environ | {"ANSIBLE_CONFIG": str(work / "ansible.cfg"),
                        "ANSIBLE_NOCOLOR": "1"}
    variables = {
        "grafana_path": str(project), "grafana_domain": "grafana.example.test",
        "letsencrypt_email": "ops@example.test", "grafana_version": "13.0.2",
        "grafana_mysql_rootpass": synthetic_value("root"), "grafana_mysql_password": synthetic_value("db"),
        "grafana_admin_password": synthetic_value("admin"), "grafana_smtp_password": synthetic_value("smtp"),
        "grafana_renderer_token": synthetic_value("renderer"),
        "grafana_datasources": [{
            "name": "primary", "uid": "stable-uid", "type": "postgres",
            "url": "db.example.test:5432", "user": "postgres",
            "secureJsonData": {"password": SECRET, "tlsClientKey": "PEM\nline2\n"},
            "password": synthetic_value("LEGACY_CANARY", "_$foo"),
            "basicAuthPassword": synthetic_value("BASIC_CANARY", "_${foo}"),
            "jsonData": {"database": "postgres", "sslmode": "disable"},
        }],
    }

    def render(check=False, fail=False):
        play = {
            "hosts": "localhost", "connection": "local", "gather_facts": False,
            "vars": variables, "roles": ["fixture"],
        }
        (work / "play.yml").write_text(yaml.safe_dump([play]))
        result = subprocess.run(
            ["ansible-playbook", "-i", "localhost,", "play.yml", "--diff"]
            + (["--check"] if check else []),
            cwd=work, env=env, text=True, capture_output=True,
        )
        output = result.stdout + result.stderr
        for canary in ("DS_CANARY", "LEGACY_CANARY", "BASIC_CANARY", "UNKNOWN_CANARY"):
            assert canary not in output, output
        assert (result.returncode != 0) == fail, output
        return output

    output = render(check=True)
    assert "stable-uid" in output and "db.example.test:5432" in output
    output = render()
    assert "stable-uid" in output
    assert (project / ".env").stat().st_mode & 0o777 == 0o600
    datasource = yaml.safe_load(provisioning.read_text())["datasources"][0]
    assert "DS_CANARY" not in provisioning.read_text()
    for value in list(datasource["secureJsonData"].values()) + [datasource["password"], datasource["basicAuthPassword"]]:
        assert value.startswith("$GRAFANA_DS_") and "{" not in value

    def compose(extra_env=None):
        # Compose config's escapeDollarSign doubles dollars when serializing its
        # resolved model, including JSON. Undo that output-only escaping.
        output = run(COMPOSE_CMD + ["-f", str(project / "docker-compose.yml"),
                                   "config", "--format", "json"],
                     cwd=project, env=os.environ | (extra_env or {}))
        return json.loads(output.replace("$$", "$"))

    config = compose()
    container_env = config["services"]["grafana"]["environment"]
    for key, value in variables["grafana_datasources"][0]["secureJsonData"].items():
        actual = container_env[datasource["secureJsonData"][key][1:]]
        assert actual == value, (repr(actual), repr(value))
    for key in ("password", "basicAuthPassword"):
        assert container_env[datasource[key][1:]] == variables["grafana_datasources"][0][key]
    assert container_env["GF_DATABASE_PASSWORD"] == variables["grafana_mysql_password"]
    assert container_env["GF_SESSION_PROVIDER_CONFIG"] == (
        "grafana:" + variables["grafana_mysql_password"] + "@tcp(grafanadb:3306)/grafana?allowNativePasswords=true"
    )
    assert config["services"]["grafana-image-renderer"]["environment"]["AUTH_TOKEN"] == variables["grafana_renderer_token"]
    name = datasource["secureJsonData"]["password"][1:]
    assert compose({name: "shell-precedence"})["services"]["grafana"]["environment"][name] == "shell-precedence"
    print("PASS: real Compose round-trip, special characters, legacy fields, existing env and shell precedence")

    output = render()
    assert "changed=0" in output, output
    variables["grafana_datasources"][0]["url"] = "new-db.example.test:5432"
    output = render(check=True)
    assert "new-db.example.test:5432" in output and "db.example.test:5432" in output
    print("PASS: immediately visible public config/check mode and idempotence")

    variables["grafana_datasources"][0]["secureJsonData"]["password"] = SECRET + "rotated"
    render()
    assert compose()["services"]["grafana"]["environment"][name] == SECRET + "rotated"
    print("PASS: rotation updates environment without exposing secret values")

    source = variables["grafana_datasources"][0]
    protected_files = [provisioning, project / ".env", project / "docker-compose.yml"]
    before_rejection = {path: path.read_bytes() for path in protected_files}

    def reject_credentials():
        output = render(fail=True)
        assert "supported secureJsonData fields" in output
        assert all(path.read_bytes() == contents for path, contents in before_rejection.items())

    unknown = synthetic_value("UNKNOWN_CANARY")
    source["jsonData"]["nested"] = [{"customToken": unknown}]
    reject_credentials()
    del source["jsonData"]["nested"]
    url = source["url"]
    for embedded in (
        urlunsplit(("https", "user:" + unknown + "@example.test", "", "", "")),
        urlunsplit(("https", "example.test", "", urlencode({"api_key": unknown}), "")),
    ):
        source["url"] = embedded
        reject_credentials()
    source["url"] = url
    source["secureJsonData"]["apiKey"] = unknown
    output = render()
    assert "apiKey" in output and "UNKNOWN_CANARY" not in provisioning.read_text()
    reference = yaml.safe_load(provisioning.read_text())["datasources"][0]["secureJsonData"]["apiKey"][1:]
    assert compose()["services"]["grafana"]["environment"][reference] == unknown
    source["jsonData"]["nested"] = [{"publicOption": "visible-nested-option"}]
    assert "visible-nested-option" in render(check=True)
    del source["jsonData"]["nested"]
    print("PASS: unsupported credentials rejected without writes; valid secureJsonData transition has no secret diff")
    print("PASS: unknown nested public metadata stays visible")

    variables["grafana_datasources"].append(copy.deepcopy(variables["grafana_datasources"][0]))
    render(fail=True)
    variables["grafana_datasources"].pop()
    print("PASS: duplicate identity is rejected without exposing secrets")

    # Reordering uses the same references, rather than list indices.
    variables["grafana_datasources"] = [variables["grafana_datasources"][0], {
        "name": "second", "secureJsonData": {"password": synthetic_value("second")},
    }]
    render()
    variables["grafana_datasources"].reverse()
    render()
    after = yaml.safe_load(provisioning.read_text())["datasources"]
    assert after[1]["secureJsonData"]["password"] == "$" + name
    variables["grafana_datasources"] = []
    render()
    assert not any(key.startswith("GRAFANA_DS_") for key in compose()["services"]["grafana"]["environment"])
    print("PASS: stable references on reorder, removed secrets leave environment")

    variables["grafana_datasources"] = [{
        "name": "traces", "uid": "traces", "type": "tempo",
        "url": "https://traces.example.test", "basicAuth": True,
        "basicAuthUser": "reader", "secureJsonData": {"basicAuthPassword": SECRET},
        "jsonData": {"tracesToLogsV2": {
            "datasourceUid": "logs", "spanStartTimeShift": "-1h",
            "tags": [{"key": "service.name", "value": "service"}],
        }},
    }]
    output = render(check=True)
    assert "https://traces.example.test" in output
    assert "tracesToLogsV2" in output and "spanStartTimeShift" in output
    print("PASS: nested trace-to-log settings remain visible")
