"""Utilities for image publishing."""

from pathlib import Path

import requests
from steam.client import SteamClient


def get_context() -> Path:
    """Return Docker build context.

    :return:
    """
    return Path(__file__).parent.resolve()


def get_image_reference(
    registry: str,
    tag: str,
) -> str:
    """Return image reference.

    :param registry:
    :param image_version:
    :return:
    """
    reference: str = f"{registry}/pfeiffermax/rust-game-server:{tag}"
    return reference


def get_rust_build_id() -> str:
    """Pull the Rust server's build ID using the Steam Client.

    :return:
    """
    client = SteamClient()
    client.anonymous_login()
    client.verbose_debug = False
    info: dict = client.get_product_info(apps=[258550], timeout=1)
    build_id: str = info["apps"][258550]["depots"]["branches"]["release"]["buildid"]
    return build_id


def tag_exists(build_id: str) -> bool:
    """Pull tag data from Docker Hub and check if tag with this build_id already exists.

    :param build_id:
    :return:
    """
    response = requests.get(
        "https://hub.docker.com/v2/namespaces/pfeiffermax/repositories/rust-game-server/tags"
    )
    response.raise_for_status()
    tags: dict = response.json()["results"]
    matching_tags: list[dict] = [tag for tag in tags if (build_id in tag["name"])]
    if matching_tags:
        return True
    else:
        return False


def create_tag(build_id: str) -> str:
    """Create the Docker image tag.

    :param build_id:
    :return:
    """
    return f"build-{build_id}"


def get_oxide_context() -> Path:
    """Return Docker build context.

    :return:
    """
    return Path(__file__).parent.resolve() / "oxide"


def get_oxide_build_id() -> str:
    """Pull the latest Oxide build ID via GitHub RestAPI.

    See: https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-the-latest-release

    :return:
    """
    response = requests.get(
        "https://api.github.com/repos/OxideMod/Oxide.Rust/releases/latest"
    )
    response.raise_for_status()
    build_id: str = response.json()["tag_name"]
    return build_id


def oxide_zip_file_url(build_id: str) -> str:
    """Get the latest Oxide release URL.

    See: https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-a-release-by-tag-name

    :return:
    """
    response = requests.get(
        f"https://api.github.com/repos/OxideMod/Oxide.Rust/releases/tags/{build_id}"
    )
    response.raise_for_status()
    asset_list: list[dict] = response.json()["assets"]
    zip_file_url: str = [  # noqa: RUF015
        item for item in asset_list if item["name"] == "Oxide.Rust-linux.zip"
    ][0]["browser_download_url"]
    return zip_file_url


def create_oxide_tag(build_id: str) -> str:
    """Create the Docker image tag for Oxide build.

    :param build_id:
    :return:
    """
    return f"oxide-build-{build_id}"
