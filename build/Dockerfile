FROM steamcmd/steamcmd:debian-bookworm

WORKDIR /srv/rust

RUN steamcmd +force_install_dir /srv/rust +login anonymous +app_update 258550 validate +quit

COPY runds.sh runds.sh

RUN chmod +x runds.sh

# server.port
EXPOSE 28015

# rcon.port
EXPOSE 28016

ENTRYPOINT ["/srv/rust/runds.sh"]
