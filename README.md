# rust-game-server-docker
This Docker image provides a [Rust](https://rust.facepunch.com/) dedicated game server.

## Docker Run
Run the Docker container:
```shell
docker run -it --publish 28015:28015/udp --publish 28016:28016/tcp rust:test 
```

## Docker Compose
A quick and easy way to run the [Rust](https://rust.facepunch.com/) server is Docker Compose.
Check out the [the example](examples%2Fdocker-compose%2Fcompose.yaml):

Fire up the [Rust](https://rust.facepunch.com/) server like that:
```shell
docker compose up
```
If want to connect to [Rust](https://rust.facepunch.com/) server console via RCON use the CLI client:
```shell
docker compose run -it rcon-cli
```
