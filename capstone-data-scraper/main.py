import os
from os.path import isfile
import sys

from DataScraper import DataScraper
import concurrent.futures
import logging.config
import logging
from typing import List, Tuple
from PIL import Image

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("scraper")


def get_search_keys(path: str) -> List[List[str]]:
    if not os.path.exists(path):
        raise Exception(f"{path} for search terms not found")
    with open(path, "r") as f:
        return [s.strip("\n").split(",") for s in f.readlines()]


def scraper(search_params: List[str]):
    search_key, folder_key = search_params
    folder_key = folder_key.strip()
    image_path = os.path.normpath(os.path.join(os.getcwd(), 'training-data'))
    data_scraper = DataScraper(image_path=image_path,
                               search_key=search_key,
                               headless=True,
                               folder_key=folder_key)
    image_links = data_scraper.find_image_urls()
    data_scraper.save_images(image_links)
    folder_path = os.path.normpath(os.path.join(os.getcwd(), "training-data", folder_key))
    crop_images(folder_path, (512, 512))


def crop_images(path: str, size: Tuple[int, int]) -> None:
    if not os.path.exists(path):
        raise Exception(f"{path} not found")
    filenames = [name for name in os.listdir(path + "/")]
    for filename in filenames:
        os.listdir(path)
        filepath = os.path.join(path, filename)
        image = Image.open(filepath)
        image = image.resize(size)
        image = image.convert("RGB")
        image.save(filepath, image.format)


if __name__ == "__main__":
    search_keys = get_search_keys("searchterms.txt")
    logger.info(f"Found {len(search_keys)} search keys: {search_keys}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(scraper, search_keys)
    sys.exit()
