import shutil

from AgriSatelliteModules import ManageImageries
from common_logger import logger


def main():

    image_manager_obj = ManageImageries.ManageSatelliteImages()
    logger.info(image_manager_obj.zipped_files)

    list_resolutions = [10, 20, 60]

    for zip_file in image_manager_obj.zipped_files:
        for resolution in list_resolutions[:2]:
            root_name_dir = image_manager_obj.extract_images_in_zip(zip_file, resolution=resolution)
            # TODO: If directory exists ignore clipping
            ManageImageries.clip_images_in_dir(root_name_dir, resolution=resolution,
                                               clip_geojson="vectors/cut_poly.geojson")
            shutil.rmtree(root_name_dir)
            logger.info("{} resolution {} done".format(zip_file, resolution))

    # Plot Bands with matplotlib
    ManageImageries.plot_images(dir_name="clipped_images/20210301", resolution=20, poly_cut="vectors/cut_poly.geojson")

    # # TODO: add a function to create a mosaic from all the images in the directory
    # geotiff_lst, dates, bands = image_manager_obj.create_cube_with_clipped_images_in_dir('clipped_images')
    # logger.info(sorted(bands))
    # logger.info(dates)


if __name__ == '__main__':
    main()
