"""Publish CLI."""

from pathlib import Path

import click
from python_on_whales import DockerClient

from build.constants import PLATFORMS
from build.utils import (
    create_tag,
    get_context,
    get_image_reference,
    get_podman_client,
    get_rust_build_id,
    tag_exists,
)


@click.command()
@click.option(
    "--docker-hub-username",
    envvar="DOCKER_HUB_USERNAME",
    help="Docker Hub username",
)
@click.option(
    "--docker-hub-token",
    envvar="DOCKER_HUB_TOKEN",
    help="Docker Hub token",
)
@click.option(
    "--registry", envvar="REGISTRY", default="docker.io", help="Docker registry"
)
@click.option(
    "--publish-manually",
    envvar="PUBLISH_MANUALLY",
    is_flag=True,
    help="Flag for building the Docker image manually, "
    "overrides the check for existing image tags",
)
def main(
    docker_hub_username: str,
    docker_hub_token: str,
    registry: str,
    publish_manually: bool,
) -> None:
    """Build and publish image to Docker Hub.

    :param docker_hub_username:
    :param docker_hub_token:
    :param registry:
    :param publish_manually:
    :return:
    """
    context: Path = get_context()

    click.echo("Checking Rust server build ID for release branch...")
    current_rust_server_build_id = get_rust_build_id()
    click.echo(f"Current Rust server build ID: {current_rust_server_build_id}")

    if not publish_manually and tag_exists(current_rust_server_build_id):
        click.echo(
            "Image for this build ID already exists. Skipping Docker image build..."
        )
    else:
        click.echo("Building Rust server Docker image...")

        tag = create_tag(current_rust_server_build_id)
        image_reference_version: str = get_image_reference(registry, tag)
        image_reference_latest: str = get_image_reference(registry, "latest")

        podman_client: DockerClient = get_podman_client()

        podman_client.login(
            server=registry,
            username=docker_hub_username,
            password=docker_hub_token,
        )

        # Podman has no --push flag on build, so build and push separately.
        # stream_logs=True keeps python_on_whales from inspecting buildx
        # builders, which Podman's buildx compatibility alias does not provide.
        build_log_stream = podman_client.buildx.build(
            context_path=context,
            target="production-image",
            tags=[image_reference_version, image_reference_latest],
            platforms=PLATFORMS,
            stream_logs=True,
        )
        for log_line in build_log_stream:
            click.echo(log_line, nl=False)

        # Push the tags one at a time. python_on_whales pushes an iterable of
        # tags concurrently, which makes Podman upload the layers shared by both
        # tags to the registry in parallel; the registry then drops the racing
        # blob uploads ("use of closed network connection").
        click.echo("Pushing Rust server container image...")
        podman_client.push(image_reference_version)
        podman_client.push(image_reference_latest)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
