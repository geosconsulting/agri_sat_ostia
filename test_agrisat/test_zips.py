import os

import pytest
from zipfile import ZipFile
from AgriSatelliteModules import ManageImageries


@pytest.fixture
def zip_object():
    """
    Test implementation of object for managing zip files.
    """
    zip_obj = ManageImageries.ManageSatelliteImages('../zipfiles')

    return zip_obj


def test_files_in_zip(zip_object):
    """
    Test that the files in the zip file are correct.    """

    assert len(zip_object.zipped_files) == 14


def test_content_zip_file(zip_object):
    """
    Test that the content of the zip file is correct.    """
    zip_object.get_files_in_zip(zip_object.zipped_files[0])

    # assert ['T32TQM_20210301T100031_B02_10m.jp2', 'T32TQM_20210301T100031_B03_10m.jp2'] in


