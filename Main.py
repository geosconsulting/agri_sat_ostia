import shutil

from AgriSatelliteModules import ManageImageries
from common_logger import logger


def main():

    image_manager_obj = ManageImageries.ManageSatelliteImages()
    logger.info(image_manager_obj.zipped_files)

    # list_resolutions = [10, 20, 60]

    # for zip_file in image_manager_obj.zipped_files:
    #     for resolution in list_resolutions[:2]:
    #         root_name_dir = image_manager_obj.extract_images_in_zip(zip_file, resolution=resolution)
    #         ManageImageries.clip_images_in_dir(root_name_dir, "cut_poly.shp")
    #         shutil.rmtree(root_name_dir)

    geotiff_lst, dates, bands = image_manager_obj.create_cube_with_clipped_images_in_dir('clipped_images')
    logger.info(sorted(bands))
    logger.info(dates)


if __name__ == '__main__':
    main()
