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
- `roles/<role>/` contains the collection's first-party roles; `plugins/` contains collection plugins. Usage examples live in each role's README; there is no `playbooks/` or `examples/` directory.
- `ansible.cfg`, `.ansible-lint`, and `.yamllint` define local tool settings. Check them before overriding paths or interpreting lint failures. `ansible.cfg` refers to local-only paths (`inventory/`, `roles_galaxy/`, `collections/`) that are not part of the repository; never commit them.
- This checkout has no dedicated test runner or root `requirements.yml`. Validation focuses on role linting, rendered configuration, and collection packaging.
- `.ansible-lint` runs offline. When lint needs a missing external collection, install it into the configured path with `pipenv run ansible-galaxy collection install <namespace.name> -p collections`.

## Change and verification workflow

1. Inspect the working tree and the affected role's defaults, README, tasks, templates, and handlers. Preserve unrelated user changes.
2. Make the smallest change that meets the current requirement. Update the role interface and documentation together.
3. Run the relevant checks from the repository root:

   ```bash
   pipenv run ansible-lint roles/<role>
   pipenv run yamllint roles/<role>
   git diff --check
   ```

   Add any changed YAML file outside the role to the `yamllint` call. For changes across roles, use `pipenv run ansible-lint roles/*` and `pipenv run yamllint .`.
4. When configuration behavior changes, validate it as described in [Lint and validation](docs/CONVENTIONS.md#lint-and-validation). Ask before long-running verification or building a custom proof harness.
5. Report which checks ran, what was not verified, and any missing dependencies or pre-existing failures.

For collection packaging changes, build outside the working tree:

```bash
pipenv run ansible-galaxy collection build --output-path <artifact-directory>
```

## Secrets

- Keep secret values out of chat, command arguments, logs, commits, and verification output. Follow the secrets conventions for sensitive tasks and rendered files.

## Dependencies and worktrees

- Declare Python dependencies in `Pipfile` and update `Pipfile.lock` when requirements change. `pipenv sync` installs the lockfile; it does not regenerate it.
- Declare collection dependencies needed by consumers in `galaxy.yml`; document role-specific requirements in the role README. Do not assume dependencies are vendored here.
- Pipenv chooses its virtualenv by the Pipfile's directory. To reuse the main checkout's environment from a worktree, set `PIPENV_PIPFILE=<main-checkout>/Pipfile` and keep the worktree as the working directory. Do not do this when the branch changes `Pipfile` or `Pipfile.lock`; run `pipenv sync` in the worktree instead so checks use the branch's dependencies.

## Git and release workflow

- Use a feature branch and review the staged diff before committing. Stage task-related paths rather than unrelated working-tree changes.
- Changes to roles, plugins, or collection metadata bump `version` in `galaxy.yml` in the same PR, following semantic versioning: patch for fixes, minor for new features or variables, major for breaking changes. Follow-up commits on a PR that already bumps the version keep that bump.
- Changes limited to documentation (`AGENTS.md`, `docs/`, README files) need no version bump; they ship with the next release.
- Rewrite published history only when requested. Use `git push --force-with-lease` for an approved force push.
- This repository is the upstream collection. Create or update a GitHub PR here when requested.
