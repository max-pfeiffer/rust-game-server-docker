# Podman compose on a remote builder

Runs a locally built Rust game server image on a remote Podman host (e.g. a
linux/amd64 build machine) with `podman compose`, driven from your local
machine. This is useful for testing an image build before publishing it,
especially from an arm64 machine: the install stage runs `steamcmd`, a 32-bit
x86 binary that cannot be emulated sensibly on arm64, so the image is
linux/amd64 only.

## Prerequisites

- A Podman [system connection](https://docs.podman.io/en/latest/markdown/podman-system-connection.html)
  to a linux/amd64 host (called `remotebuilder` below):
  `podman system connection list`
- A compose provider installed locally (`docker-compose` or `podman-compose`),
  see `podman compose --help`.
- With the `docker-compose` provider, two extra pieces of host setup, because
  docker-compose dials its own plain ssh connection instead of using the
  Podman connection settings:
  - An `~/.ssh/config` entry on the local machine for the remote host with
    the ssh key of the Podman connection and connection multiplexing
    (docker-compose opens many parallel ssh sessions, which trips sshd rate
    limiting otherwise):

    ```
    Host 192.168.40.20
        user builder
        IdentityFile ~/.ssh/podman_builder_ed25519
        IdentitiesOnly yes
        ControlMaster auto
        ControlPath ~/.ssh/control-%r@%h-%p
        ControlPersist 10m
    ```

  - A `docker` command on the remote host: docker-compose connects by running
    `docker system dial-stdio` over ssh. Podman implements `system dial-stdio`,
    so the official shim package is enough (on Fedora:
    `sudo dnf install podman-docker`).
- The image built on the remote host:

  ```shell
  podman --connection remotebuilder build --tag rust-game-server:test build
  ```

  The compose file defaults to `localhost/rust-game-server:test`; set the
  `RUST_IMAGE` environment variable to use a different tag.

## Usage

`podman compose` passes the selected connection through to the compose
provider, so everything runs on the remote host:

```shell
cd examples/podman-compose-remote-builder
podman --connection remotebuilder compose up -d
podman --connection remotebuilder compose logs -f rust-server
```

The `init-container` service just chowns the server data volume to the
unprivileged container user (UID 10001) and exits.

The first startup downloads the map and world data and takes a few minutes. The
ports are published on the remote host, so connect the game client to
`<remote host>:28015` and RCON to `<remote host>:28016`.

Tear down with:

```shell
podman --connection remotebuilder compose down       # add -v to also delete the server data volume
```