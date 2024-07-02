[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![pipeline workflow](https://github.com/max-pfeiffer/rust-game-server-docker/actions/workflows/pipeline.yaml/badge.svg)
![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/pfeiffermax/rust-game-server?sort=semver)
![Docker Pulls](https://img.shields.io/docker/pulls/pfeiffermax/rust-game-server)

# Rust Game Server - Docker Image
This Docker image provides a [Rust](https://rust.facepunch.com/) dedicated game server.

Facepunch releases a [new game update](https://rust.facepunch.com/changes) for the Rust community on a monthly basis
every first Thursday. Each update requires players and servers to update their versions of the game.

I will add some automation, so new images are build every first Thursday.

**Docker Hub:** https://hub.docker.com/r/pfeiffermax/rust-game-server

**GitHub Repository:** https://github.com/max-pfeiffer/rust-game-server-docker

## Usage
You can append all server configuration options as commands when running `RustDedicated` binary.  

### Docker Run
For instance run the Docker container like this:
```shell
docker run -it --publish 28015:28015/udp --publish 28016:28016/tcp pfeiffermax/rust-game-server:2024-06-23 +server.ip 0.0.0.0 +server.port 28015 +rcon.ip 0.0.0.0 +rcon.port 28016
```

### Docker Compose
With Docker Compose you have you can fire up your own [Rust](https://rust.facepunch.com/) server in no-time. For this, just clone this repo
(or just copy and paste the [compose.yaml](examples/docker-compose/compose.yaml) file to your machine) and run the server with Docker compose like this:
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

If you want to connect to [Rust](https://rust.facepunch.com/) server console via RCON use the CLI client:
```shell
docker compose run -it --rm rcon-cli
[+] Creating 1/0
 ✔ Container rust-server  Running                                                                                                                                             0.0s 
Waiting commands for rust-server:28016 (or type :q to exit)
> 
```

### Production Deployment
If you want to deploy to a production (Linux) server, have a look at the [compose.yaml](examples%2Fdocker-compose-production%2Fcompose.yaml)
in the Docker Compose production example.

## Additional Information Sources
* [Official Rust Wiki](https://wiki.facepunch.com/rust/)
* [Valve Wiki](https://developer.valvesoftware.com/wiki/Rust_Dedicated_Server)
* [Admin commands list](https://www.corrosionhour.com/rust-admin-commands/)
