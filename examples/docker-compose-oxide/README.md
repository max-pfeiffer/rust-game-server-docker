# Docker Compose example with Oxide

This example runs the [Oxide](https://umod.org/games/rust) (uMod) variant of the Rust
dedicated game server with Docker Compose. On top of the server it also starts a
[web RCON client](https://github.com/max-pfeiffer/rust-web-rcon) and a
[file manager](https://github.com/max-pfeiffer/file-manager) web app so you can install
and configure Oxide plugins straight from your browser — no shell access or FTP needed.

The Oxide image (`pfeiffermax/rust-game-server:latest-oxide`) layers the Oxide mod files
on top of the base `pfeiffermax/rust-game-server` image. On first start Oxide creates its
`oxide/` directory tree inside the server, which is persisted here in the `oxide` Docker
volume so your plugins, configs and data survive restarts and image updates.

## Usage

Clone the repo and start everything:

```shell
git clone https://github.com/max-pfeiffer/rust-game-server-docker.git
cd rust-game-server-docker/examples/docker-compose-oxide
docker compose up -d
```

The first startup downloads the map and world data and takes a few minutes. Follow the
logs with:

```shell
docker compose logs -f rust-server
```

Stop and tear everything down (add `-v` to also delete the `oxide` and server data volumes):

```shell
docker compose down
```

## Services

| Service | Image | Purpose |
| --- | --- | --- |
| `init-container` | `alpine` | Chowns the server data volume to the unprivileged container user (UID/GID 10001) and exits. Since v2.0.0 the server runs as user `rust`, not root. |
| `rust-server` | `pfeiffermax/rust-game-server:latest-oxide` | The Rust dedicated server with Oxide. Game port `28015/udp`, RCON port `28016/tcp`. |
| `rust-web-rcon` | `pfeiffermax/rust-web-rcon:latest` | Browser-based RCON console, published on port `80`. |
| `file-manager` | `pfeiffermax/file-manager:latest` | Web file browser rooted at the `oxide` volume, published on port `8080`. Used to manage plugins and configs. |

Server settings (hostname, world size, RCON password, etc.) are passed as `+server.*` /
`+rcon.*` arguments in the `command:` list of the `rust-server` service in
[`compose.yaml`](./compose.yaml). Edit them there and re-run `docker compose up -d`.

### Web RCON

Point your browser at http://localhost, then enter the server address and the RCON
password (`supersecret` in this example — change it in `compose.yaml`) to reach the Rust
server console and statistics.

## Installing Oxide plugins

Oxide expects plugins and their supporting files under the server's `oxide/` directory:

| Directory | Contents |
| --- | --- |
| `oxide/plugins` | Plugin `.cs` source files — this is where you drop plugins to install them |
| `oxide/config` | Per-plugin JSON configuration files (generated on first load) |
| `oxide/data` | Plugin data storage |
| `oxide/lang` | Localization / language files |
| `oxide/logs` | Plugin error and debug logs |

In this Compose setup that whole tree lives in the `oxide` Docker volume, which is mounted
at `/srv/rust/oxide` in both the `rust-server` and `file-manager` containers. The
file-manager's `FILES_ROOT` is set to `/srv/rust/oxide`, so its web UI is rooted exactly at
Oxide's directory.

To install a plugin (see the [official uMod guide](https://docs.oxidemod.com/guides/owners/install-plugins)):

1. Download the plugin's `.cs` file (for example from [uMod](https://umod.org/plugins)).
2. Open the file manager at http://localhost:8080 and browse into the `plugins` folder.
3. Upload the `.cs` file there.

Oxide watches `oxide/plugins` and **compiles and loads new or changed plugins
automatically** — you do not need to restart the server. Watch `docker compose logs -f
rust-server` (or the web RCON console) for a message confirming the plugin loaded. You can
also reload a plugin manually from the RCON console with `oxide.reload <PluginName>`.

Removing a plugin's `.cs` file from `oxide/plugins` (via the file manager) unloads it.

## Configuring Oxide plugins

Most plugins generate a JSON configuration file under `oxide/config` the first time they
load — for example `oxide/config/MyPlugin.json`. To customize a plugin:

1. In the file manager (http://localhost:8080), browse into the `config` folder.
2. Open the plugin's `.json` file and edit it in the browser, then save.
3. Apply the changes by reloading the plugin from the web RCON console:
   `oxide.reload MyPlugin`. Many plugins also pick up config changes automatically.

Plugins that store persistent state (e.g. player data) keep it under `oxide/data`, and
translatable text lives under `oxide/lang` — both are editable through the same file
manager.

## Security note

For simplicity the file manager runs with `AUTH_METHOD: none`, meaning **anyone who can
reach port `8080` has full read/write access** to your Oxide files. This is fine for local
testing on a trusted machine. Before exposing this setup to a network, protect the file
manager — it also supports HTTP basic auth and Keycloak/OIDC. Set, for example:

```yaml
    environment:
      AUTH_METHOD: "basic"
      AUTH_USERNAME: "admin"
      AUTH_PASSWORD: "change-me"
      FILES_ROOT: "/srv/rust/oxide"
```

See the [file-manager documentation](https://github.com/max-pfeiffer/file-manager) for the
full list of options.
