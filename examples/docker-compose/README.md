# Simple Docker Compose example
This example contains a simple docker compose file for running the Rust server on your machine (MacOS, Windows, Linux).

It demonstrates the usage of a [Docker Volume](https://docs.docker.com/storage/volumes/) to persist the Rust server data.

## Usage
Clone the repo and start the Rust server:
```shell
git clone https://github.com/max-pfeiffer/rust-game-server-docker.git
cd rust-game-server-docker/examples/docker-compose
docker compose up -d
```
Stop the server:
```shell
docker compose down
```
And show the logs, option `-f` follows the logs:
```shell
docker compose logs -f
```

## Rust WebSocket Rcon
When spinning up the containers with Docker compose, an instance of the
[Rust Websocket RCon client](https://github.com/max-pfeiffer/rust-web-rcon) is started as well.

If you want to connect to [Rust](https://rust.facepunch.com/) server console or want to check on the server statistics,
just point your web browser to: http://localhost

Then enter the address of your server and the Rcon password in the web interface. 
