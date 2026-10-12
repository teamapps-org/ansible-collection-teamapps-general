# Conventions

These conventions apply to developing reusable roles in the `teamapps.general` collection. Deployments and site-specific configuration belong to the Ansible projects that consume it.

Follow official Ansible and ansible-lint guidance unless an intentional local deviation is recorded below. Apply these rules to new and changed code; keep unrelated legacy migrations out of the same change.

The [public repository boundary in AGENTS.md](../AGENTS.md#public-repository-boundary) applies to every contribution. Use generic placeholders in examples and keep consumer-specific information in the consuming project.

## Role interfaces and composition

- Use lowercase `snake_case` for role names and role-prefixed variables, such as `webproxy_*`. Prefix registered results and internal variables as well to avoid collisions between roles.
- Declare every configurable input in `roles/<role>/defaults/main.yml`, including required inputs with no default value. Document shared variables consumed by the role. Ansible facts, registered results, and task-local helpers are not configurable defaults.
- Keep interfaces small. Add a toggle, alternate backend, or compatibility path only for a current use case.
- Keep reusable behavior in roles. Consuming projects supply site-specific hosts, domains, credentials, and overrides.
- Use the standard role layout: `tasks/`, `defaults/`, `handlers/`, `templates/`, and `files/` as needed. Add only used files and directories.
- Prefer `import_tasks` for static composition and `include_tasks` for dynamic composition. Split task files at clear functional boundaries, not to create one-task wrappers. Avoid include chains deeper than one level without a clear reason.
- Name role files in `snake_case`, such as `tasks/zpool.yml`. Files deployed to a target keep their upstream names, such as `docker-compose.yml`.
- Order tasks as preflight validation, setup, configuration, then service management.
- Use fully qualified collection role names in consumer examples, such as `teamapps.general.webproxy`.

## Tasks, idempotence, and check mode

- Name every task and play. Use short descriptive task names, sentence case or lowercase, without trailing punctuation. Name handlers for the action they perform.
- Prefer idempotent modules over `shell` and `command`. Set explicit `state` values where supported.
- For command-like tasks, make change reporting match actual behavior. Use `changed_when: false` for read-only probes and detect changes for mutating commands.
- Use `failed_when` only when native module failure handling does not describe the expected outcome.
- After a successful run, a second run should normally report zero changes unless external state changed.
- Preserve check mode. Use `check_mode: false` only for read-only probes that must run during validation; document nonstandard behavior.
- Use `| bool` for conditions on values that may be strings. Use a named `loop_control.loop_var` when the loop variable has domain meaning or nested tasks could collide.
- Quote paths and variables in shell commands. Use explicit ownership and quoted file modes, such as `'0640'` and `'0750'`.
- Validate required or paired inputs before writing files or changing services. Error messages should name the inputs without printing secret values.

## YAML, Jinja, and module names

- Use `.yml` for Ansible-authored YAML. Deployed files may retain upstream extensions and names.
- Use 2-space indentation, lowercase `true` and `false`, and aligned list/map nesting. Follow `.yamllint` for exact formatting.
- Preserve existing document-start markers; new files do not require `---`.
- Use one space after `#` in comments and keep long lines readable even though line length is not enforced.
- Quote YAML strings containing Jinja expressions. Use explicit `default(...)` arguments.
- Merge and transform dictionaries with `combine`, `dict2items`, and `items2dict` as existing roles do, rather than with custom loops or `set_fact` chains.
- Keep templates readable. Put configurable policy in defaults and keep heavy data preparation out of templates.
- Put templates in `templates/` with a `.j2` suffix and static files in `files/`.
- Serialize values for the target format instead of hand-quoting credentials or arbitrary strings. Account for both Compose and application interpolation when dollar signs are literal data.
- Builtin modules may keep short names, such as `copy` and `cron`. External collection modules use fully qualified names, such as `community.docker.docker_compose_v2`. `.ansible-lint` skips both `fqcn-builtins` and `fqcn[action]`, so lint does not catch a missing collection prefix; check it in review.
- Sort unordered long lists where useful for review. Preserve execution order and precedence-sensitive lists.

## Secrets

- Commit placeholders or encrypted values, never plaintext credentials. In consumer inventories, prefer individually encrypted Ansible Vault values so variable names remain visible.
- Use `no_log: true` on tasks that render, read, or report secret values. Protect debug output, assertion failures, and application validation output too.
- Keep secrets out of endpoint URLs and ordinary configuration diffs. Separate secret-bearing files from non-secret configuration when the application supports it.
- Set secret-file ownership and permissions explicitly. Prefer root-owned mode `'0600'`; use a restricted group and mode `'0640'` only when a non-root service must read the file. Mount container secret files read-only.
- For Compose interpolation, write a project `.env` file with mode `'0600'` and `no_log: true`, then reference `${VARIABLE}` in `docker-compose.yml`. Pass required container environment values explicitly through `environment:` rather than loading the whole file with `env_file:`. The vmauth services in `victoriametrics` and `victorialogs` still use `env_file:`; keep that unless the change is about their secret handling.
- If an application supports file-based credentials or a secrets/config overlay, prefer that over injecting credentials into the container environment. The webproxy collector's separate secrets overlay is one example.
- Keep ordinary config tasks and diffs visible when they contain no secrets. Document diff exposure when changing secret-bearing file layouts: old inline values can appear in removal diffs.
- Read secret input privately or through Vault. Avoid literal secrets in shell arguments and command history.

## Docker Compose services

- Use `restart: always` for new long-running services and `restart: "no"` for one-shot jobs. Some existing services use `unless-stopped` or `on-failure`; leave them unless the change is about restart behavior.
- Add a meaningful healthcheck to each new long-running service. Use a documented endpoint or command; ask the maintainers if the correct probe is unknown.
- Leave architecture selection to the image unless the role requires a specific `platform:`.
- Expose host-side bind addresses and ports through role defaults when they are part of the service interface.
- Expose image versions as role defaults, such as `<role>_version`. Pin new defaults to a specific release tag rather than `latest`. Many existing roles default to `latest`; change that only as part of a deliberate version update for that role.
- Let `community.docker.docker_compose_v2` with `state: present` apply Compose changes. It recreates services whose configuration changed; the Compose template task does not need a restart notification.
- Bind-mounted configuration and secret files are not part of Compose's configuration hash. Notify a handler when the application must reload or restart after those files change.
- Scope reload/restart handlers to affected services with `services:`. A single-service change must not restart an entire project, especially its databases or migration jobs.

## Authentication and authorization

- Successful provider login alone is not access control. Restrict protected services to explicit groups or application roles and document the chosen claim mode.
- Use dedicated access-control groups rather than broad directory roles or unrelated collaboration groups.
- For OAuth2 Proxy role behavior, group filtering, and session storage, follow [roles/oauth2_proxy/README.md](../roles/oauth2_proxy/README.md). Keep tenant IDs, registrations, and actual group assignments in consumer configuration.
- Provider-side restrictions must be explicit. Creating an OAuth application inside a GitLab group does not by itself restrict who can log in.

## Examples and tags

- Role READMEs hold the usage examples. Keep them minimal but runnable with their documented requirements. Target a named host/group or an explicit placeholder instead of unconstrained `hosts: all`.
- Use tags where selective execution is useful. Prefer role-prefixed task tags; functional tags remain valid.
- Propagate tags through dynamic includes with `apply` when included tasks must inherit them.

## Documentation

- Keep each role's README about its reusable design, requirements, configurable inputs, examples, check-mode behavior, and lifecycle limitations.
- Document new defaults in the role README and explain behavior changes. Link to defaults and implementation for exact details instead of duplicating entire files.
- Collection-wide contributor guidance belongs here; agent workflow belongs in [AGENTS.md](../AGENTS.md). Site-specific topology and operational procedures belong in the consumer repository.
- Keep agent handovers and transient workspace state out of project documentation. Use ignored local context files instead.

## Lint and validation

- Run `ansible-lint` on changed roles and `yamllint` on changed YAML through pipenv. The commands are in the README's [Run checks](../README.md#run-checks) section.
- Respect `.ansible-lint` and `.yamllint`. For a necessary one-off exception, use a narrow `# noqa rule-name` with a reason. Preserve existing exceptions unless the task includes removing them; use local exceptions rather than adding new `skip_ansible_lint` tags or global skips.
- Validate rendered configuration with the application's own validator where possible. Check the enabled, disabled, and authentication variants affected by the change.
- Check repeat-run idempotence and check-mode behavior when practical.
- State in the PR what was verified and what was not. A collection build checks packaging; lint and check mode do not replace runtime verification.

## References

- [Ansible roles](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Ansible check and diff modes](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html)
- [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [ansible-lint rules](https://docs.ansible.com/projects/lint/rules/)
