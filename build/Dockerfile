FROM steamcmd/steamcmd:debian-trixie AS install-stage

RUN steamcmd +force_install_dir /srv/rust +login anonymous +app_update 258550 validate +quit

FROM debian:trixie-slim AS production-image

# Principle of least privilege: create a new user for running the application
RUN groupadd -g 10001 rust && \
    useradd -r -u 10001 -g rust --create-home rust


# We need netcat for readiness and liveness probes
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    ca-certificates \
    netcat-traditional \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/rust
RUN chown rust:rust /srv/rust

COPY --from=install-stage --chown=rust:rust /srv/rust /srv/rust

COPY --chown=rust:rust runds.sh /srv/rust/runds.sh
RUN chmod +x /srv/rust/runds.sh

# server.port, rcon.port udp, rcon.port tcp, queryport, app.port
EXPOSE 28015/udp 28016/udp 28016/tcp 28017/udp 28082/tcp

# Use the unpriviledged user to run the application
USER 10001

ENTRYPOINT ["/srv/rust/runds.sh"]
