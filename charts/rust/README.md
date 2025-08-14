# Rust Helm Chart
A [Helm chart](https://helm.sh/) for running a Rust dedicated server.

## Installation
If you want to run Rust on a bare metal Kubernetes cluster, I recommend reading
[my blog post](https://max-pfeiffer.github.io/blog/hosting-game-servers-on-bare-metal-kubernetes-with-kube-vip.html)
about that topic.

### Helm
Currently, you can run a single server instance with each Helm installation. The installation is done as follows:
```shell
$ helm repo add rust https://max-pfeiffer.github.io/rust-game-server-docker
$ helm install rust rust/rust --values your_values.yaml --namespace yournamespace 
```

### Argo CD
I recommend deploying and running the Rust dedicated server with [Argo CD](https://argoproj.github.io/cd/). This way
you have a declarative installation of your server. It's very easy to manage and update it that way.
A big plus is also the [Argo CD Image Updater](https://github.com/argoproj-labs/argocd-image-updater). This tool can
monitor the [Rust Docker Image](https://hub.docker.com/r/pfeiffermax/rust-game-server) and will update your Rust
installation automatically when a new image is released.

## Configuration options
### Resources
Make sure to get the resource specs right. You will need at least two CPU cores and 8GB of RAM. There is a [RAM
estimation tool](https://developer.valvesoftware.com/wiki/Rust_Dedicated_Server#System_Requirements) that you could use.
```yaml
resources:
  limits:
    cpu: 3
    memory: 10Gi
  requests:
    cpu: 2
    memory: 8Gi
```
Especially RAM is quite critical as Kubernetes is evicting/kills the Pod when it overshoots that resource limit. So
you want to check your monitoring and adjust `resource.limits.memory` when you see that happening. It's generally a
good idea to set the limit a bit higher than what you think the Rust server will request.

### Startup Probe
Rust server startup is very slow. The larger your world size is, the more time it takes on first boot to generate the
world. Depending on your world size, you need to raise the `failureThreshold`. Multiply `periodSeconds` with
`failureThreshold` to get the maximum time for startup. These settings work for a 3000 world size:
```yaml
startupProbe:
  periodSeconds: 10
  failureThreshold: 100
```

### Rust server config
Tweak the Rust server config to your liking. 
```yaml
rustDedicatedServer:
  # You can use just one single string without any spaces as this is specified as command line option.
  hostName: "Vanilla-Rust-Server"
  # Rust main server port
  serverPort: "28015"
  # Rust Rcon port
  rconPort: "28016"
  # Rust server query port
  serverQueryPort: "28017"
  # Port for Rust+ app
  appPort: "28082"
  # Maximum number of players
  maxPlayers: "20"
  # World size
  worldSize: "3000"
  # Map seed, always use a string here as Helm number conversion might produce incompatible strings.
  seed: "666"
  # Use 1 to switch on websocket rcon, 0 to switch off websocket rcon
  rconWeb: "1"
  # Rcon Password
  rconPassword: "yourpassword"
  # Volume size for server identity directory. Rust server stores it's config, saves and blueprints there
  volumeStorageSize: "1Gi"
  # Name of the existing secret to use for the rconPassword.
  # If this is set, rustDedicatedServer.rconPassword will be ignored.
  # The existing secret needs to have stored Rust rconPassword under the key rconPassword.
  existingSecret: ""
```