# Simple Docker Compose example
This example contains a simple docker compose file for running the Rust server on your machine (MacOS, Windows, Linux).

It demonstrates the usage of a [Docker Volume](https://docs.docker.com/storage/volumes/) to persist the Rust server data.

## Usage
Clone the repo and start the Rust server:
```shell
git clone https://github.com/max-pfeiffer/rust-game-server-docker.git
docker compose up -d
```

Stop the server:
```shell
docker compose down
```
