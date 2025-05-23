"""Tests Docker image build."""

from click.testing import CliRunner, Result
from furl import furl
from requests import Response, get
from requests.auth import HTTPBasicAuth
from testcontainers.registry import DockerRegistryContainer

from build import publish
from build.oxide import publish as oxide_publish
from build.utils import (
    create_oxide_tag,
    create_tag,
    get_oxide_build_id,
    get_rust_build_id,
)
from tests.constants import LATEST_TAG, REGISTRY_PASSWORD, REGISTRY_USERNAME

BASIC_AUTH: HTTPBasicAuth = HTTPBasicAuth(REGISTRY_USERNAME, REGISTRY_PASSWORD)


def test_image_build(
    registry_container: DockerRegistryContainer,
    cli_runner: CliRunner,
):
    """Test building the Docker image.

    :param docker_client:
    :param buildx_builder:
    :return:
    """
    result: Result = cli_runner.invoke(
        publish,
        env={
            "DOCKER_HUB_USERNAME": REGISTRY_USERNAME,
            "DOCKER_HUB_PASSWORD": REGISTRY_PASSWORD,
            "REGISTRY": registry_container.get_registry(),
        },
    )
    assert result.exit_code == 0

    furl_item: furl = furl(f"http://{registry_container.get_registry()}")
    furl_item.path /= "v2/_catalog"

    response: Response = get(furl_item.url, auth=BASIC_AUTH)

    assert response.status_code == 200
    assert response.json() == {"repositories": ["pfeiffermax/rust-game-server"]}

    furl_item: furl = furl(f"http://{registry_container.get_registry()}")
    furl_item.path /= "v2/pfeiffermax/rust-game-server/tags/list"

    response: Response = get(furl_item.url, auth=BASIC_AUTH)

    assert response.status_code == 200

    response_image_tags: list[str] = response.json()["tags"]

    current_rust_server_build_id = get_rust_build_id()
    tag = create_tag(current_rust_server_build_id)

    assert not {tag, LATEST_TAG}.difference(set(response_image_tags))


def test_oxide_image_build(
    registry_container: DockerRegistryContainer,
    cli_runner: CliRunner,
):
    """Test building the Docker image.

    :param docker_client:
    :param buildx_builder:
    :return:
    """
    result: Result = cli_runner.invoke(
        oxide_publish,
        env={
            "DOCKER_HUB_USERNAME": REGISTRY_USERNAME,
            "DOCKER_HUB_PASSWORD": REGISTRY_PASSWORD,
            "REGISTRY": registry_container.get_registry(),
        },
    )
    assert result.exit_code == 0

    furl_item: furl = furl(f"http://{registry_container.get_registry()}")
    furl_item.path /= "v2/_catalog"

    response: Response = get(furl_item.url, auth=BASIC_AUTH)

    assert response.status_code == 200
    assert response.json() == {"repositories": ["pfeiffermax/rust-game-server"]}

    furl_item: furl = furl(f"http://{registry_container.get_registry()}")
    furl_item.path /= "v2/pfeiffermax/rust-game-server/tags/list"

    response: Response = get(furl_item.url, auth=BASIC_AUTH)

    assert response.status_code == 200

    response_image_tags: list[str] = response.json()["tags"]

    current_oxide_build_id = get_oxide_build_id()
    tag = create_oxide_tag(current_oxide_build_id)

    assert not {tag, LATEST_TAG}.difference(set(response_image_tags))
