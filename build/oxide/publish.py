"""Publish CLI."""

from os import getenv
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
    docker_hub_token: str,
    registry: str,
    publish_manually: bool,
) -> None:
    """Build and publish image to Docker Hub.

    :param docker_hub_token:
    :param registry:
    :return:
    """
    github_ref_name: str = getenv("GITHUB_REF_NAME")
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
        if github_ref_name:
            cache_to: str = f"type=gha,mode=max,scope={github_ref_name}"
            cache_from: str = f"type=gha,scope={github_ref_name}"
        else:
            cache_to = f"type=local,mode=max,dest=/tmp,scope={github_ref_name}"
            cache_from = f"type=local,src=/tmp,scope={github_ref_name}"

        docker_client: DockerClient = DockerClient()
        builder: Builder = docker_client.buildx.create(
            driver="docker-container", driver_options=dict(network="host")
        )

        docker_client.login(
            server=registry,
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
            cache_to=cache_to,
            cache_from=cache_from,
            push=True,
        )

        # Cleanup
        docker_client.buildx.stop(builder)
        docker_client.buildx.remove(builder)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
