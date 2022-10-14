import os
import sys
import concurrent.futures
import logging.config
import logging
from typing import List, Tuple
from PIL import Image
from DataScraper import DataScraper



logging.config.fileConfig("logging.conf")
logger = logging.getLogger("scraper")

IMAGE_MIN_SIZE = (512, 512)
SAVE_FOLDER = f"training_data_{IMAGE_MIN_SIZE[0]}"


def get_search_keys(path: str) -> List[List[str]]:
    if not os.path.exists(path):
        raise Exception(f"{path} for search terms not found")
    with open(path, "r") as f:
        return [s.strip("\n").split(",") for s in f.readlines()]


def scraper(search_params: List[str]):
    search_key, folder_key = search_params
    folder_key = folder_key.strip()
    image_path = os.path.normpath(os.path.join(os.getcwd(), SAVE_FOLDER)) 
    data_scraper = DataScraper(image_path=image_path,
                               search_key=search_key,
                               headless=False,
                               folder_key=folder_key,
                               max_images=1000,
                               delay = 0.5)
    image_links = data_scraper.find_image_urls()
    logger.info(f"Found {len(image_links)} for {search_key}")
    saved_percentage = data_scraper.save_images(image_links, verbose=True)
    logger.info(f"Saved {saved_percentage}% from {len(image_links)} for search key {search_key}")
    folder_path = os.path.normpath(os.path.join(image_path, folder_key))
    crop_images(folder_path, IMAGE_MIN_SIZE)

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

def main() -> None:
    search_keys = get_search_keys("searchterms.txt")
    logger.info(f"Found {len(search_keys)} search keys: {search_keys}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(scraper, search_keys)
    sys.exit()

if __name__ == "__main__":
   main()
