"""Tests building the container images and publishing them to a registry."""

from build.oxide.publish import main as oxide_main
from build.publish import main
from build.utils import (
    create_oxide_tag,
    create_tag,
    get_oxide_build_id,
    get_rust_build_id,
)
from click.testing import CliRunner, Result
from furl import furl
from requests import Response, get

from tests.constants import REGISTRY_TOKEN, REGISTRY_USERNAME


def test_image_build(
    registry: str,
    cli_runner: CliRunner,
):
    """Test building the base Rust server image and publishing it.

    :param registry:
    :param cli_runner:
    :return:
    """
    result: Result = cli_runner.invoke(
        main,
        env={
            "DOCKER_HUB_USERNAME": REGISTRY_USERNAME,
            "DOCKER_HUB_TOKEN": REGISTRY_TOKEN,
            "REGISTRY": registry,
            "PUBLISH_MANUALLY": "1",
        },
    )
    assert result.exit_code == 0, result.output

    catalog_url: furl = furl(f"http://{registry}")
    catalog_url.path /= "v2/_catalog"

    response: Response = get(catalog_url.url)

    assert response.status_code == 200
    assert response.json() == {"repositories": ["pfeiffermax/rust-game-server"]}

    tags_url: furl = furl(f"http://{registry}")
    tags_url.path /= "v2/pfeiffermax/rust-game-server/tags/list"

    response = get(tags_url.url)
    assert response.status_code == 200

    response_image_tags: list[str] = response.json()["tags"]

    tag = create_tag(get_rust_build_id())

    assert tag in response_image_tags
    assert "latest" in response_image_tags


def test_oxide_image_build(
    registry: str,
    cli_runner: CliRunner,
):
    """Test building the Oxide Rust server image and publishing it.

    :param registry:
    :param cli_runner:
    :return:
    """
    result: Result = cli_runner.invoke(
        oxide_main,
        env={
            "DOCKER_HUB_USERNAME": REGISTRY_USERNAME,
            "DOCKER_HUB_TOKEN": REGISTRY_TOKEN,
            "REGISTRY": registry,
            "PUBLISH_MANUALLY": "1",
        },
    )
    assert result.exit_code == 0, result.output

    catalog_url: furl = furl(f"http://{registry}")
    catalog_url.path /= "v2/_catalog"

    response: Response = get(catalog_url.url)

    assert response.status_code == 200
    assert response.json() == {"repositories": ["pfeiffermax/rust-game-server"]}

    tags_url: furl = furl(f"http://{registry}")
    tags_url.path /= "v2/pfeiffermax/rust-game-server/tags/list"

    response = get(tags_url.url)
    assert response.status_code == 200

    response_image_tags: list[str] = response.json()["tags"]

    tag = create_oxide_tag(get_oxide_build_id())

    assert tag in response_image_tags
    assert "latest-oxide" in response_image_tags
