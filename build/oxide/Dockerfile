FROM debian:bookworm-slim AS mod-stage
ARG OXIDE_ZIP_FILE_URL

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    wget \
    unzip \
    ca-certificates

WORKDIR /tmp/oxide

# Offical Oxide docs: https://docs.oxidemod.com/guides/owners/install-oxide
RUN wget ${OXIDE_ZIP_FILE_URL} -O oxide.zip && unzip oxide.zip

FROM pfeiffermax/rust-game-server:latest AS production-image

USER 0

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    # Needed for Sign Artist Plugin: https://umod.org/plugins/sign-artist
    libgdiplus \
    && rm -rf /var/lib/apt/lists/*

COPY --from=mod-stage --chown=rust:rust /tmp/oxide/RustDedicated_Data /srv/rust/RustDedicated_Data/

USER 10001