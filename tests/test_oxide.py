"""Tests."""

from build.utils import oxide_zip_file_url


def test_oxide():
    """Test release URL.

    :return:
    """
    release = oxide_zip_file_url()
    assert release
