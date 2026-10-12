# AGENTS.md

This repository publishes the `teamapps.general` Ansible collection. Keep roles generic and reusable. Deployments belong to the Ansible projects that consume the collection.

## Public repository boundary

- Never include consumer organization names, internal system information, actual hostnames or IP addresses, private domains or URLs, tenant or account identifiers, ticket references, or other site-specific details.
- Apply this rule to code, comments, examples, documentation, filenames, commit messages, and PR content.
- Use generic placeholders such as `app.example.com` and documentation-only addresses. Keep real configuration and operational context in the consuming Ansible project.
- Public upstream project names, package names, and official documentation links are permitted when required to identify an integration or dependency.

Before creating or changing roles, playbooks, templates, or plugins, read [docs/CONVENTIONS.md](docs/CONVENTIONS.md). It is the source of truth for coding, secrets, Compose, and documentation conventions. This file covers agent workflow and repository-specific tooling.

## Environment and repository facts

- Run Python and Ansible tools through `pipenv run`, or inside an active pipenv shell. `Pipfile` declares the Python version and dependencies; `Pipfile.lock` records resolved versions.
- Bootstrap with `pipenv sync`. Confirm the installed Ansible version with `pipenv run ansible --version`.
- `roles/<role>/` contains the collection's first-party roles; `plugins/` contains collection plugins. `playbooks/` and `examples/` contain usage examples.
- `ansible.cfg`, `.ansible-lint`, and `.yamllint` define local tool settings. Check them before overriding paths or interpreting lint failures.
- This checkout has no dedicated test runner or root `requirements.yml`. Validation focuses on role linting, rendered configuration, and collection packaging.
- `.ansible-lint` runs offline. Install missing external collections in the configured collection path only when needed for the task.

## Change and verification workflow

1. Inspect the working tree and the affected role's defaults, README, tasks, templates, and handlers. Preserve unrelated user changes.
2. Make the smallest change that meets the current requirement. Update the role interface and documentation together.
3. Run the relevant checks from the repository root:

   ```bash
   pipenv run ansible-lint roles/<role>
   pipenv run yamllint roles/<role>/tasks/main.yml
   git diff --check
   ```

   Include every changed YAML file in the YAML check. For broader changes, use `pipenv run ansible-lint roles/*` and `pipenv run yamllint .`.
4. When configuration behavior changes, validate rendered files with the application's own validator where available. Check repeat-run idempotence and check-mode behavior when practical. Prefer existing checks; ask before long-running verification or building a custom proof harness.
5. Report which checks ran and any limits, missing dependencies, or pre-existing failures. Lint success alone does not prove role behavior.

For collection packaging changes, build outside the working tree:

```bash
pipenv run ansible-galaxy collection build --output-path <artifact-directory>
```

## Secrets

- Keep secret values out of chat, command arguments, logs, commits, and verification output. Follow the secrets conventions for sensitive tasks and rendered files.

## Dependencies and worktrees

- Declare Python dependencies in `Pipfile` and update `Pipfile.lock` when requirements change. `pipenv sync` installs the lockfile; it does not regenerate it.
- Declare collection dependencies needed by consumers in `galaxy.yml`; document role-specific requirements in the role README. Do not assume dependencies are vendored here.
- Pipenv chooses its virtualenv by the Pipfile's directory. To reuse the main checkout's environment from a worktree, set `PIPENV_PIPFILE=<main-checkout>/Pipfile`. Keep the current worktree as the command's working directory.

## Git and release workflow

- Use a feature branch and review the staged diff before committing. Stage task-related paths rather than unrelated working-tree changes.
- Before pushing release changes, update `version` in `galaxy.yml`. Keep an existing PR's version bump when adding follow-up fixes; documentation-only changes do not require another bump.
- Rewrite published history only when requested. Use `git push --force-with-lease` for an approved force push.
- This repository is the upstream collection. Create or update a GitHub PR here when requested.
