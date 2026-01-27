# AGENTS.md

This repository is an Ansible collection (`teamapps.general`) with many roles.
Use these notes when making changes so your edits fit existing practices.

## Environment and tooling

- Python: 3.10 (see `Pipfile`)
- Package manager: `pipenv`
- Ansible config: `ansible.cfg` in repo root

### Bootstrap

```bash
pipenv sync
pipenv shell
```

## Build, lint, and test

There is no dedicated test runner in this repo; linting is the primary check.
The collection can be built with `ansible-galaxy` when needed.

### Lint all roles

```bash
ansible-lint roles/*
```

### Lint a single role ("single test")

```bash
ansible-lint roles/zfs
ansible-lint roles/hetzner_robot
```

### YAML lint (all YAML files)

```bash
yamllint .
```

### YAML lint a single file ("single test")

```bash
yamllint roles/zfs/tasks/main.yml
```

### Build the collection tarball

```bash
ansible-galaxy collection build
```

### Install collection locally (optional)

```bash
ansible-galaxy collection install -r requirements.yml -f
```

Notes:

- `ansible-lint` config: `.ansible-lint`
- `yamllint` config: `.yamllint`
- Some roles add `skip_ansible_lint` tags intentionally.

## Repository structure

- `roles/<role>`: standard role layout (`defaults/`, `tasks/`, `handlers/`, `templates/`, `files/`)
- `playbooks/`: example playbooks
- `plugins/`: collection plugins (filters, modules, etc.)
- `examples/`: user examples

## Code style guidelines

### YAML and formatting

- Indentation: 2 spaces (see `.yamllint`)
- No document start marker (`---`), unless a file already uses it
- Line length is not enforced, but keep lines readable
- Keep a single space after `#` in comments
- Use lists with `-` and align nested maps under the key

### Ansible tasks

- Always include a `name` for tasks, short and lowercase (verb first)
- Prefer idempotent modules over shell/command
- Use `changed_when` and `check_mode` when behavior is non-standard
- Use `tags` when tasks are logically grouped
- Use `when` with explicit boolean checks (`| bool`) when a fact may be stringy
- Use `loop_control.loop_var` when the item name matters

### Variables and defaults

- Role variables are prefixed with the role name (e.g. `zfs_`, `hetzner_robot_`)
- Role defaults live in `defaults/main.yml`
- All role variables MUST be documented in role defaults.
- Keep default values explicit and documented with comments when helpful
- Booleans are lowercase `true`/`false`

### Jinja and templating

- Use Jinja in YAML strings with `"{{ ... }}"` or `'{{ ... }}'`
- Prefer `| default(...)` instead of `| default` to be explicit
- Use `| combine` and `| dict2items` as in existing roles
- Keep Jinja expressions on one line when possible

### Module naming and FQCN

- Builtin modules are typically referenced without FQCN (e.g. `copy`, `cron`)
- Community modules use FQCN (e.g. `community.general.zfs_delegate_admin`)
- This repo skips ansible-lint FQCN rules; follow existing style

### Error handling and safety

- Use `failed_when` only when needed; prefer native module checks
- Guard tasks with `when` to avoid unexpected changes
- Avoid unsafe defaults; set conservative permissions (e.g. `mode: '0750'`)
- For shell scripts, keep paths explicit and quote variables in commands

### Naming conventions

- Task names: sentence case or lowercase, no trailing period
- Variables: snake_case, role-prefixed
- Files: snake_case where possible (`main.yml`, `zpool.yml`)
- Handlers: descriptive verbs ("restart service")

### Role composition

- Use `import_tasks` for static includes, `include_tasks` for dynamic
- When including tasks with tags, use `apply` to propagate tags
- Avoid deep include chains without a clear reason

### Templates and files

- Templates live in `templates/` with `.j2` suffix
- Files live in `files/` and are copied with `copy`
- Keep templates readable; avoid heavy logic when variables can precompute values

### Documentation

- Each role keeps a `README.md` with usage and variables
- Update role README when adding new defaults or behavior
- Keep examples minimal but accurate

## Existing agent rules

- No Cursor or Copilot rules found in `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md`.

## Practical tips

- Run `ansible-lint` on the specific role you touched before opening a PR.
- If you add new role defaults, mirror them in the role README.
- Keep tasks ordered: preflight checks → setup → configuration → services.
- Before release (git push), update the version in `galaxy.yml`.
