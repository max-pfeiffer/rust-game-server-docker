[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/max-pfeiffer/rust-game-server-docker/graph/badge.svg?token=RfzYdxhvCd)](https://codecov.io/gh/max-pfeiffer/rust-game-server-docker)
[![Code Quality](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/code-quality.yaml/badge.svg)](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/code-quality.yaml)
[![Test Image Build](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/test-image-build.yaml/badge.svg)](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/test-image-build.yaml)
[![Publish Docker Image](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/publish.yaml/badge.svg)](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/publish.yaml)
[![Lint Helm Chart](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/helm-lint.yaml/badge.svg)](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/helm-lint.yaml)
[![Release Helm Charts](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/helm-release.yaml/badge.svg)](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/helm-release.yaml)
![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/pfeiffermax/rust-game-server?sort=semver)
![Docker Pulls](https://img.shields.io/docker/pulls/pfeiffermax/rust-game-server)

# Rust Dedicated Game Server - Docker Image and Helm chart
This Docker image provides a [Rust](https://rust.facepunch.com/) dedicated game server. You will find here also a
[Helm Chart](https://helm.sh/) for running a Rust dedicated server on [Kubernetes container orchestration system](https://kubernetes.io/). 

[Facepunch](https://facepunch.com/) releases an [update](https://rust.facepunch.com/changes) for Rust monthly every
first Thursday. Also, there are irregular updates every now and then. Each update requires players and servers to
update their versions of the game.

Therefore, an automation checks the [Rust release branch](https://steamdb.info/app/258550/depots/?branch=release) every
night. If a new release was published by [Facepunch](https://facepunch.com/), a new Docker image will be built with this
new version. Just use the `latest` tag and you will always have an up-to-date Docker image.

Kudus to:
* [@jonakoudijs](https://github.com/jonakoudijs) for providing the [Steamcmd Docker image](https://github.com/steamcmd/docker) which is used here
* [@detiam](https://github.com/detiam) for maintaining a working fork for the [Steam websocket client](https://github.com/detiam/steam_websocket) 

**Docker Hub:** https://hub.docker.com/r/pfeiffermax/rust-game-server

**GitHub Repository:** https://github.com/max-pfeiffer/rust-game-server-docker

## IMPORTANT CHANGE SINCE V2.0.0 (build-21954779, 18.2.2026)
Since image version V2.0.0 the application is run with an unprivileged user and not with root user anymore. This was
done to improve the security of this image.
If you were persisting server identity with a Volume and start the Rust dedicated server using the new image (like
in the docker compose examples), you will encounter problems starting your server. This happens because root user still
owns the files in that Volume and the new unprivileged user doesn't have permissions to access these files.

If you are using Docker please adjust the file ownership with this command:
```shell
docker exec -it -u root rust-server chown -R rust:rust /srv/rust
```
Please restart the Docker container afterwards. Your server should start up just fine.
`rust-server` is the name of your container.

If you are using the Helm chart for running the Rust dedicated server on Kubernetes, just upgrade your Helm release
using chart version v2.2.0 or newer. This will fix file permissions in your Volume by applying the correct `fsGroup`
for the Pod security context.

## Oxide
Since v1.1.0 I provide an [Oxide](https://umod.org/games/rust) variant of this image. The automation checks for
[a new Oxide release on GitHub](https://github.com/OxideMod/Oxide.Rust/releases) every night and builds a new image
based on the latest version of my Rust Docker image.

The tag of these images is prefixed with `oxide-build`. So look out for these
[tags on Docker Hub](https://hub.docker.com/r/pfeiffermax/rust-game-server/tags) if you want to run Rust with Oxide.
There is also a `latest-oxide` tag, so you can use this to always run an up-to-date Docker image with Oxide.

This image aims to be a solid base to run any plugin. So please drop me a line if you are missing any Debian package
for a plugin.

## Rust Websocket Rcon
If you want to connect to [Rust](https://rust.facepunch.com/) server console or want to check on the server statistics,
check out my [Rust Websocket Rcon client](https://github.com/max-pfeiffer/rust-web-rcon) companion project.
I provide a Docker container with [Facepunch's websocket Rcon client](https://github.com/Facepunch/webrcon).
This is already integrated in the docker compose examples.

## Usage
### Configuration
You can append all [server configuration options](https://www.corrosionhour.com/rust-admin-commands/) as commands
when running `RustDedicated` binary. Use the regular syntax like `+server.ip 0.0.0.0` or `-logfile`.

As the Rust server is running in the Docker container as a stateless application, you want to have all stateful server
data (map, config, blueprints, etc.) stored in a [Docker volume](https://docs.docker.com/storage/volumes/)
which is persisted outside of the container. This can be configured with `+server.identity`: you can specify the
directory where this data is stored. You need to make sure that this directory is mounted on
a [Docker Volume](https://docs.docker.com/storage/volumes/).

This is especially important because you need to update the Rust server Docker image every month when Facepunch
releases a new software update. When you use a [Docker volume](https://docs.docker.com/storage/volumes/) to store
the `+server.identity`, all the data is still intact.

Check out the [docker compose](examples/docker-compose/README.md) and the
[docker compose production](examples/docker-compose-production/README.md) examples to learn about
the details. 

### Docker Run
For testing purposes, you can fire up a Docker container like this:
```shell
docker run -it --publish 28015:28015/udp --publish 28016:28016/tcp pfeiffermax/rust-game-server:latest +server.ip 0.0.0.0 +server.port 28015 +rcon.ip 0.0.0.0 +rcon.port 28016
```

### Docker Compose
With docker compose you have your own [Rust](https://rust.facepunch.com/) server up and running in no-time. For this,
just clone this repo (or just copy and paste the [compose.yaml](examples/docker-compose/compose.yaml) file to your
machine) and run the server with Docker compose like this:
```shell
git clone https://github.com/max-pfeiffer/rust-game-server-docker.git
cd rust-game-server-docker/examples/docker-compose
docker compose up
```
You can also run the [Rust](https://rust.facepunch.com/) server in the background with option `-d`:
```shell
docker compose up -d
```
And show the logs, option `-f` follows the logs:
```shell
docker compose logs -f
```

#### Rust Websocket Rcon
When spinning up the containers with Docker compose, an instance of the
[Rust Websocket RCon client](https://github.com/max-pfeiffer/rust-web-rcon) is started as well.

If you want to connect to [Rust](https://rust.facepunch.com/) server console or want to check on the server statistics,
point your web browser to: http://localhost

Then enter the address of your server and the Rcon password in the web interface. 

### Production Deployment
If you want to deploy to a production (Linux) server, have a look at the
[docker compose production example documentation](examples/docker-compose-production/README.md).

## Helm chart
If you would like to run the Rust server in your [Kubernetes](https://kubernetes.io/) cluster, I provide a
[Helm chart](https://helm.sh/) you could use: [https://max-pfeiffer.github.io/rust-game-server-docker](https://max-pfeiffer.github.io/rust-game-server-docker)

There is also [documentation available](charts/rust/README.md) for that Helm chart.

If you want to run your Rust server on bare metal Kubernetes, check out
[my blog article](https://max-pfeiffer.github.io/blog/hosting-game-servers-on-bare-metal-kubernetes-with-kube-vip.html)
on how to do that using [kube-vip](https://kube-vip.io/).

## Additional Information Sources
* [SteamDB](https://steamdb.info/app/258550/info/)
* [Official Rust Wiki](https://wiki.facepunch.com/rust/)
* [Valve Wiki](https://developer.valvesoftware.com/wiki/Rust_Dedicated_Server)
* [Admin commands list](https://www.corrosionhour.com/rust-admin-commands/)

## Other Game Server Projects
* [Valheim dedicated server](https://github.com/max-pfeiffer/valheim-dedicated-server-docker-helm)