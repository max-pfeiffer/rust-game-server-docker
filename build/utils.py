"""Utilities for image publishing."""

from pathlib import Path


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
