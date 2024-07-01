"""Basic test fixtures."""

import pytest
from python_on_whales import Builder, DockerClient


@pytest.fixture(scope="session")
def docker_client() -> DockerClient:
    """Provide the Python on Whales docker client.

    :return:
    """
    return DockerClient(debug=True)


@pytest.fixture(scope="session")
def buildx_builder(docker_client: DockerClient) -> Builder:
    """Provide a Pyhton on Whales BuildX builder instance.

    :param docker_client:
    :return:
    """
    builder: Builder = docker_client.buildx.create(
        driver="docker-container", driver_options=dict(network="host")
    )
    yield builder
    docker_client.buildx.stop(builder)
    docker_client.buildx.remove(builder)
