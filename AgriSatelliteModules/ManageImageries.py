import os
import re
import shutil
from datetime import datetime
from typing import List
from zipfile import ZipFile
import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from pathlib import Path
import xarray as xr

# Custom Modules
from common_logger import logger


def get_coordinates(gdf_curr):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf_curr.to_json())['features'][0]['geometry']]


def clip_images_in_dir(root_name_dir: str, clip_geojson: str) -> None:

    new_dir = f"clipped_images/{root_name_dir}"
    Path(new_dir).mkdir(parents=True, exist_ok=True)

    logger.info('Clipping images in {}'.format(root_name_dir))

    # Read images
    images = []
    for f in os.listdir(root_name_dir):
        if f.endswith('.jp2'):
            images.append(f)

    # Read and reproject geojson
    clip_shape = gpd.read_file(clip_geojson)

    # Loop over images
    for image in images:
        logger.info('Clipping {}'.format(image))

        # Read image
        with rasterio.open(os.path.join(root_name_dir, image)) as src:
            # Read image
            image_array = src.read(1)
            # Get image metadata
            image_meta = src.meta.copy()
            # Get image crs
            image_crs = src.crs
            # Get image transform
            image_transform = src.transform
            # Get image bounds
            image_bounds = src.bounds

            clip_shape = clip_shape.to_crs(image_crs)
            coords = get_coordinates(clip_shape)

            # Clip image
            clipped_image, clipped_image_transform = mask(src, coords, crop=True)

            # fig, ax = plt.subplots(figsize=(5, 6))
            # show(clipped_image, ax=ax, cmap="Blues")
            # plt.show()

            image_meta.update({"driver": "GTiff",
                               "height": clipped_image.shape[1],
                               "width": clipped_image.shape[2],
                               "transform": clipped_image_transform})

            # Create new image
            with rasterio.open(os.path.join(new_dir, image), 'w', **image_meta) as dst:
                # save the resulting raster
                dst.write(clipped_image)


class ManageSatelliteImages:
    """ Class to unzip extract and clip Sentinel2 satellite images """

    def __init__(self, zipdir='zipfiles'):
        self.zipdir = zipdir
        self.zipped_files = self.get_zipped_files()

    def get_zipped_files(self):
        zip_files = []
        for f in os.listdir(self.zipdir):
            if f.endswith('.zip'):
                zip_files.append(f)
        return zip_files

    def get_files_in_zip(self, single_zip_file: str) -> list:

        zip_obj = ZipFile(os.path.join(self.zipdir, single_zip_file))

        return zip_obj.namelist()

    def extract_images_in_zip(self, single_zip_file: str, resolution: list[int] = 20) -> str:

        current_name_dir = single_zip_file.split('.')[0][-22:-7]
        os.mkdir(current_name_dir)
        logger.info('Managing images for {}'.format(current_name_dir))

        with ZipFile(os.path.join(self.zipdir, single_zip_file)) as zip_file:
            # Iterate over the file names
            for member in zip_file.namelist():
                filename = os.path.basename(member)
                if not filename:
                    continue

                if f'IMG_DATA/R{resolution}m/T' in member:
                    if member.endswith('.jp2'):
                        search_string = member.split('/')[-1].split('.')[0][-7:]
                        x = re.findall(f"B?[0-9]_{resolution}m$", search_string)
                        if x:
                            # Extract a single file from zip
                            # zip_file.extract(member, root_name_dir)
                            source = zip_file.open(member)
                            target = open(os.path.join(current_name_dir, filename), "wb")
                            with source, target:
                                shutil.copyfileobj(source, target)
                            logger.info('Extracting {}'.format(filename))

        return current_name_dir

    def create_cube_with_clipped_images_in_dir(self, root_name_dir: str) -> List[str]:

        geotiff_list = []
        geotiff_list_dates = []
        geotiff_list_bands = []

        for path, subdirs, files in os.walk(root_name_dir):
            for name in files:
                if name.endswith('.jp2'):
                    geotiff_list.append(os.path.join(path, name))
                    string_no_ext = name.split('.')[0]
                    date_str = string_no_ext.split('_')[-3][0:8]
                    date_date = datetime.strptime(date_str, '%Y%m%d')
                    geotiff_list_dates.append(date_date)
                    band = string_no_ext.split('_')[-2]
                    geotiff_list_bands.append(band)
                    # print(date_date, band)

        # Create variable used for time axis
        date_date_unique = set(geotiff_list_dates)
        date_bands_unique = set(geotiff_list_bands)

        # time_var = xr.Variable('time', geotiff_list,string_slice=(12, -4)))

        return geotiff_list, date_date_unique, date_bands_unique

