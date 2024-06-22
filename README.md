# rust-game-server-docker
This Docker image provides a Rust dedicated game server.

## Usage
Run the docker container:
```shell
docker run -it --publish 28015:28015 --publish 28016:28016 rust:test 
```

If you want to use docker compose check out [the example](examples%2Fdocker-compose%2Fcompose.yaml).
