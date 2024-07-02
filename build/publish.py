"""Publish CLI."""

from os import getenv
from pathlib import Path

import click
from python_on_whales import Builder, DockerClient

from build.constants import PLATFORMS
from build.utils import get_context, get_image_reference


@click.command()
@click.option(
    "--docker-hub-username",
    envvar="DOCKER_HUB_USERNAME",
    help="Docker Hub username",
)
@click.option(
    "--docker-hub-password",
    envvar="DOCKER_HUB_PASSWORD",
    help="Docker Hub password",
)
@click.option("--version", envvar="VERSION", required=True, help="Image Version")
@click.option(
    "--registry", envvar="REGISTRY", default="docker.io", help="Docker registry"
)
def main(
    docker_hub_username: str,
    docker_hub_password: str,
    version: str,
    registry: str,
) -> None:
    """Build and publish image to Docker Hub.

    :param docker_hub_username:
    :param docker_hub_password:
    :param version:
    :param registry:
    :return:
    """
    github_ref_name: str = getenv("GITHUB_REF_NAME")
    context: Path = get_context()
    image_reference_version: str = get_image_reference(registry, version)
    image_reference_latest: str = get_image_reference(registry, "latest")
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
        username=docker_hub_username,
        password=docker_hub_password,
    )

    docker_client.buildx.build(
        context_path=context,
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
