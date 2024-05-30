FROM steamcmd/steamcmd:debian-bookworm

WORKDIR /rust

RUN steamcmd +force_install_dir /rust +login anonymous +app_update 258550 validate +quit

RUN chmod +x /rust/runds.sh

EXPOSE 28015

ENTRYPOINT ["runds.sh"]
