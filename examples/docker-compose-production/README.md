# Docker Compose Example for Production Use
This example demonstrates the usage of the Rust server Docker image for production use on a Linux Server.
It also can be utilised to run multiple Rust servers on one host.

It contains the following features:
* configures resource usage (CPU, memory)
* sets the `pull_policy` to always, so docker compose always pulls the `latest` image when firing up the server
* utilises a [Docker Volume](https://docs.docker.com/storage/volumes/) to persist the Rust server data
* creates a bind mount for the log file to make it accessible on the host system
* uses an .env file to store secrets and configuration

## Usage
Clone the repo and create the .env file:
```shell
git clone https://github.com/max-pfeiffer/rust-game-server-docker.git
cd examples/docker-compose-production
cp .env-example .env
```
Edit the `.env` file to your liking.

Start the server (create and start the container):
```shell
docker compose up -d
```

Stop the server (stop and remove containers, networks):
```shell
docker compose down
```

## Automation
As Facepunch releases an update every month, you need to update your Rust server as well. So you need a new, updated
Rust server image.

As the docker compose file uses the `latest` tag for the Rust server image, the only thing you need to do is
stopping/removing and creating/starting the container with docker compose. Docker then pulls the up-to-date Rust server
image and starts the server. And you are done with your server update. :smiley: 

For instance, you can automate this with a cron job. Check out [rust-server-update.sh](rust-server-update.sh), which is
a simple script you can add as a daily job to your `/etc/crontab`. That way you ensure your server is always up-to-date. 

## Rust Websocket Rcon
When spinning up the containers with Docker compose, an instance of the
[Rust Websocket RCon client](https://github.com/max-pfeiffer/rust-web-rcon) is started as well.

If you want to connect to [Rust](https://rust.facepunch.com/) server console or want to check on the server statistics,
just point your web browser to: http://localhost

Then enter the address of your server and the Rcon password in the web interface. 
