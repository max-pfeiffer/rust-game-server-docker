# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Despite the name, this is **not** a Rust application. It is Python build automation plus a
multi-stage Dockerfile that produces and publishes a [Rust dedicated game server](https://rust.facepunch.com/)
Docker image (`pfeiffermax/rust-game-server`), together with a Helm chart for running it on Kubernetes.

The Python code's only job is to decide *whether* a new image is needed and to drive `podman`
(via the [python-on-whales](https://gabrieldemarmiesse.github.io/python-on-whales/) client) to
build and push it. There is no long-running service here.

## Common commands

Dependency management is [uv](https://github.com/astral-sh/uv); Python 3.11+. The project is
non-packaged (`[tool.uv] package = false`), so nothing installs a root package — `uv sync` just
builds the environment from `uv.lock`.

```shell
uv sync --group dev                                # install everything incl. test deps
uv run pytest                                      # run the test suite
uv run pytest --cov build --cov-report=xml         # with coverage (as CI runs it)
uv run pytest tests/test_image_build.py::test_image_build   # a single test
uv run pre-commit run -a                           # lint + format (ruff-check --fix, ruff-format)
```

Building/publishing an image locally (mirrors the `docker-image` workflow):

```shell
# PUBLISH_MANUALLY=1 bypasses the "tag already exists" short-circuit
PUBLISH_MANUALLY=1 uv run python -m build.publish         # base Rust image
PUBLISH_MANUALLY=1 uv run python -m build.oxide.publish   # Oxide variant
```

The `steam[client]` dependency comes from a git fork pinned in `[tool.uv.sources]`, so resolving
the lockfile requires network access to GitHub.

**The tests require Podman** (no Docker daemon). `conftest.py` runs a throwaway `registry:2`
container via Podman on port 5000 and the publish CLIs `podman push` the built image into it, so
mark `localhost:5000` insecure in `registries.conf.d` (HTTP-only). The build targets `linux/amd64`
and the install stage runs steamcmd, a 32-bit x86 binary that **cannot be emulated on arm64** — so
on an Apple-silicon machine the fixtures resolve a Podman *system connection* to an amd64 host
(export `PODMAN_CONNECTION`, or add an amd64 connection with `podman system connection add`), and
`build/utils.py:get_podman_client` routes every `podman` call through it. The tests are slow and
download the full Rust server via steamcmd. Ruff is scoped to `build/` and `tests/` only (`charts/` and
`examples/` are excluded).

## Architecture

### Image publishing (`build/`)

Two nearly-parallel [Click](https://click.palletsprojects.com/) CLIs share helpers in `build/utils.py`:

- `build/publish.py` — the base image. Queries the current Rust server **build ID** from Steam
  (`get_rust_build_id`, anonymous Steam client on app `258550`), and unless `--publish-manually`
  is set, skips the build entirely if a matching tag already exists on Docker Hub (`tag_exists`).
  Otherwise it logs in, runs `podman build` on the `production-image` target (`legacy_build`), and
  `podman push`es both the versioned tag (`build-<id>`) and `latest`.
- `build/oxide/publish.py` — the [Oxide](https://umod.org/games/rust) variant. Same flow keyed on
  the latest Oxide GitHub release (`get_oxide_build_id`), passing the release zip URL as the
  `OXIDE_ZIP_FILE_URL` build arg and pushing `oxide-build-<id>` + `latest-oxide`.

This build-ID-diffing is the core idea: the nightly `publish` workflow runs both, and each is a no-op
unless upstream (Facepunch / OxideMod) actually shipped something new.

### Runtime image (`build/Dockerfile`, `build/oxide/Dockerfile`, `build/runds.sh`)

- Base Dockerfile is two stages: `install-stage` runs `steamcmd` to install the Rust server into
  `/srv/rust`, then `production-image` copies it into a slim Debian image. **Since v2.0.0 the server
  runs as the unprivileged user `rust` (uid/gid 10001), not root** — this is a recurring source of
  volume-permission issues for users upgrading (see README); preserve it.
- The Oxide Dockerfile layers on top of the published base image (`FROM pfeiffermax/rust-game-server:latest`)
  and overlays the Oxide files.
- `runds.sh` is the entrypoint. It optionally sources env files pointed to by `CONFIG_FILE_PATH` and
  `SECRET_FILE_PATH` (populated by the Helm chart's ConfigMap/Secret), runs `envsubst` over each CLI
  argument so Helm-templated `+server.*` values expand, then execs `RustDedicated -batchmode -nographics "$@"`.

### Helm chart (`charts/rust/`)

A StatefulSet-based chart (ConfigMap for server config, Secret for the RCON password, an init container
to fix volume `fsGroup` ownership for the unprivileged user). Documented in `charts/rust/README.md`.
Not covered by the Python tests or ruff.

### CI (`.github/workflows/`)

`publish.yaml` (nightly cron) chains base then Oxide via the reusable `docker-image.yaml` /
`oxide-docker-image.yaml`. `test-image-build.yaml` and `code-quality.yaml` run on PRs that touch
`build/`, `tests/`, `.github/`, or `uv.lock`. Helm chart lint/release are separate workflows.
The `setup-environment` composite action installs uv and Python via `astral-sh/setup-uv`.
