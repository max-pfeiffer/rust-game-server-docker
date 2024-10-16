"""Tests."""

from build.utils import latest_oxide_release_url


def test_oxide():
    """Test release URL.

    :return:
    """
    release = latest_oxide_release_url()
    assert release
