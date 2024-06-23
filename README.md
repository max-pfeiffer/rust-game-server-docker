# rust-game-server-docker
This Docker image provides a [Rust](https://rust.facepunch.com/) dedicated game server.

Facepunch releases a [new game update](https://rust.facepunch.com/changes) for the Rust community on a monthly basis
every first Thursday. Each update requires players and servers to update their versions of the game.

I will add some automation, so new images are build every first Thursday.

## Usage
You can append all server configuration options as commands when running `RustDedicated` binary.  

### Docker Run
For instance run the Docker container like this:
```shell
docker run -it --publish 28015:28015/udp --publish 28016:28016/tcp pfeiffermax/rust-game-server:2024-06-23 +server.ip 0.0.0.0 +server.port 28015
```

### Docker Compose
A quick and easy way to run the [Rust](https://rust.facepunch.com/) server is Docker Compose.
Check out the [the example](examples%2Fdocker-compose%2Fcompose.yaml):

Fire up the [Rust](https://rust.facepunch.com/) server:
```shell
docker compose up
```
If want to connect to [Rust](https://rust.facepunch.com/) server console via RCON use the CLI client:
```shell
docker compose run -it rcon-cli
```
