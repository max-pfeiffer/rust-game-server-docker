FROM steamcmd/steamcmd:debian-bookworm

# We need netcat for readiness and liveness probes
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    netcat-traditional

WORKDIR /srv/rust

RUN steamcmd +force_install_dir /srv/rust +login anonymous +app_update 258550 validate +quit

COPY runds.sh runds.sh

RUN chmod +x runds.sh

# server.port, rcon.port udp, rcon.port tcp, queryport, app.port
EXPOSE 28015/udp 28016/udp, 28016/tcp, 28017/udp, 28082/tcp

ENTRYPOINT ["/srv/rust/runds.sh"]
