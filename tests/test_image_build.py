"""Tests Docker image build."""

from click.testing import CliRunner, Result
from furl import furl
from python_on_whales import DockerClient
from requests import Response, get
from requests.auth import HTTPBasicAuth
from testcontainers.registry import DockerRegistryContainer

from build.oxide.publish import main as oxide_main
from build.publish import main
from build.utils import (
    create_oxide_tag,
    create_tag,
    get_oxide_build_id,
    get_rust_build_id,
)
from tests.constants import REGISTRY_PASSWORD, REGISTRY_USERNAME

BASIC_AUTH: HTTPBasicAuth = HTTPBasicAuth(REGISTRY_USERNAME, REGISTRY_PASSWORD)


def test_image_build(
    registry_container: DockerRegistryContainer,
    cli_runner: CliRunner,
    docker_client: DockerClient,
):
    """Test building the Docker image.

    :param registry_container:
    :param cli_runner:
    :param docker_client:
    :return:
    """
    result: Result = cli_runner.invoke(
        main,
        env={
            "DOCKER_HUB_USERNAME": REGISTRY_USERNAME,
            "DOCKER_HUB_PASSWORD": REGISTRY_PASSWORD,
            "REGISTRY": registry_container.get_registry(),
            "PUBLISH_MANUALLY": "1",
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

    assert not {tag, "latest"}.difference(set(response_image_tags))

    # with docker_client.run("pfeiffermax/rust-game-server:latest", command=COMMANDS)
    # as rust_container:
    #     test = rust_container.state


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
        oxide_main,
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

    assert not {tag, "latest-oxide"}.difference(set(response_image_tags))
