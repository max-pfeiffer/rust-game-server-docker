"""Publish CLI."""

from pathlib import Path

import click
from python_on_whales import Builder, DockerClient

from build.constants import PLATFORMS
from build.utils import (
    create_oxide_tag,
    get_image_reference,
    get_oxide_build_id,
    get_oxide_context,
    oxide_zip_file_url,
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
    :return:
    """
    context: Path = get_oxide_context()

    click.echo("Checking Oxide build ID for release branch...")
    current_oxide_build_id = get_oxide_build_id()
    click.echo(f"Current Oxide build ID: {current_oxide_build_id}")

    if not publish_manually and tag_exists(current_oxide_build_id):
        click.echo(
            "Image for this build ID already exists. Skipping Docker image build..."
        )
    else:
        click.echo("Building Oxide mod Docker image...")

        tag = create_oxide_tag(current_oxide_build_id)
        image_reference_version: str = get_image_reference(registry, tag)
        image_reference_latest: str = get_image_reference(registry, "latest-oxide")

        docker_client: DockerClient = DockerClient()
        builder: Builder = docker_client.buildx.create(
            driver="docker-container", driver_options=dict(network="host")
        )

        docker_client.login(
            server=registry,
            username=docker_hub_username,
            password=docker_hub_token,
        )

        docker_client.buildx.build(
            context_path=context,
            build_args={
                "OXIDE_ZIP_FILE_URL": oxide_zip_file_url(current_oxide_build_id),
            },
            target="production-image",
            tags=[image_reference_version, image_reference_latest],
            platforms=PLATFORMS,
            builder=builder,
            push=True,
        )

        # Cleanup
        docker_client.buildx.stop(builder)
        docker_client.buildx.remove(builder)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
