# Rust Helm Chart
A [Helm chart](https://helm.sh/) for running a Rust dedicated server. Since v2.0.0 this Helm chart supports running multiple
server instances using one StatefulSet. 

## Installation
If you want to run Rust on a bare metal Kubernetes cluster, I recommend reading
[my blog post](https://max-pfeiffer.github.io/blog/hosting-game-servers-on-bare-metal-kubernetes-with-kube-vip.html)
about that topic.

### Helm
You can run multiple server instance with each Helm installation. Please be aware that with a StatefulSet Kubernetes
starts additional instances only after the first instance is in ready state. And Rust server startup is slow,
so it might take a while until your Rust server fleet is up and running completely.
It might better suit your needs to install multiple StatefulSets with separate Helm releases.

The installation is done as follows:
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
### Security Context
As the `pfeiffermax/rust-game-server` image runs the Rust server with an unprivileged user since V2.0.0, secure default
values for `podSecurityContext` and `securityContext` were added.
```yaml
podSecurityContext:
  fsGroup: 10001

securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
```
If that doesn't suit your needs, just override these defaults.

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
Tweak the Rust server config to your liking. You can add a list of server to `instances`. Please be aware that the
configuration of resources and ports are shared by these instances.
```yaml
# You can choose to run multiple instances of Rust dedicated servers here.
# For a new instance add another entry to this list.
instances:
    # You can use just one single string without any spaces as this is specified as command line option.
  - hostName: "Vanilla-Rust-Server"
    # Maximum number of players
    maxPlayers: "20"
    # World size
    worldSize: "3000"
    # Game mode. Options: vanilla, softcore, hardcore, weapontest, primitive
    gameMode: "vanilla"
    # Map seed, always use a string here as Helm number conversion might produce incompatible strings.
    seed: "666"
    # Use 1 to switch on websocket rcon, 0 to switch off websocket rcon
    rconWeb: "1"
    # Rcon Password
    rconPassword: "yourpassword"
    # Pod specific service
    service:
      type: LoadBalancer
      externalTrafficPolicy: Cluster
      metadata:
        annotations: {}
```
If you want to create the Secret with the `rconPassword` not with the Helm installation, you can specify the name of
an existing secret. This is a common approach when you work with the GitOps approach and create your Secrets for
instance using the External Secrets Operator.
```yaml
rustDedicatedServer:
  # Name of the existing secret to use for the rconPassword.
  # If this is set, instances[*].rconPassword will be ignored.
  # The existing secret needs to store the passwords for all instances in this pattern (see secret template):
  # data:
  #   rust-dedicated-server-0: |
  #     rconPassword=yourpassword
  #   rust-dedicated-server-1: |
  #     rconPassword=yourpassword
  existingSecret: "mysecret"  
```
