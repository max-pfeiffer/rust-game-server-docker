"""Tests Docker image build."""

from datetime import date

from furl import furl
from python_on_whales import Builder, DockerClient
from requests import Response, get
from requests.auth import HTTPBasicAuth
from testcontainers.registry import DockerRegistryContainer

from build.constants import PLATFORMS
from build.utils import get_image_reference
from tests.constants import CONTEXT, REGISTRY_PASSWORD, REGISTRY_USERNAME

BASIC_AUTH: HTTPBasicAuth = HTTPBasicAuth(REGISTRY_USERNAME, REGISTRY_PASSWORD)


def test_image_build(
    docker_client: DockerClient,
    buildx_builder: Builder,
):
    """Test building the Docker image.

    :param docker_client:
    :param buildx_builder:
    :return:
    """
    with DockerRegistryContainer(
        username=REGISTRY_USERNAME, password=REGISTRY_PASSWORD
    ).with_bind_ports(5000, 5000) as registry_container:
        registry: str = registry_container.get_registry()
        image_reference_version: str = get_image_reference(
            registry, date.today().isoformat()
        )
        image_reference_latest: str = get_image_reference(registry, "latest")
        tags: list[str] = [image_reference_version, image_reference_latest]

        docker_client.login(
            server=registry,
            username=REGISTRY_USERNAME,
            password=REGISTRY_PASSWORD,
        )

        docker_client.buildx.build(
            context_path=CONTEXT,
            tags=tags,
            platforms=PLATFORMS,
            builder=buildx_builder,
            push=True,
        )

        # Cleanup
        docker_client.buildx.stop(buildx_builder)
        docker_client.buildx.remove(buildx_builder)

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

        assert not set(tags).difference(set(response_image_tags))
