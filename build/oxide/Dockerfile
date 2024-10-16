FROM debian:bookworm-slim as mod-stage
ARG OXIDE_ZIP_FILE_URL
ARG OXIDE_ZIP_FILE_NAME

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    wget \
    unzip

WORKDIR /tmp

RUN wget ${OXIDE_ZIP_FILE_URL} && unzip ${OXIDE_ZIP_FILE_NAME}

FROM steamcmd/steamcmd:debian-bookworm as production-stage

WORKDIR /srv/rust

RUN steamcmd +force_install_dir /srv/rust +login anonymous +app_update 258550 validate +quit

COPY runds.sh runds.sh

RUN chmod +x runds.sh

# server.port
EXPOSE 28015/udp

# rcon.port
EXPOSE 28016/tcp

ENTRYPOINT ["/srv/rust/runds.sh"]
