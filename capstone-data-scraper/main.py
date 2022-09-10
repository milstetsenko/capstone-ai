import os
import sys

from DataScraper import DataScraper
import concurrent.futures
import logging.config

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("scraper")


def get_search_keys(path: str) -> list[str]:
    if not os.path.exists(path):
        raise Exception(f"{path} for search terms not found")
    with open(path, "r") as f:
        return [s.strip("\n") for s in f.readlines()]


def scraper(search_key: str):
    image_path = os.path.normpath(os.path.join(os.getcwd(), 'training-data'))
    data_scraper = DataScraper(image_path=image_path,
                               search_key=search_key,
                               headless=True)
    image_links = data_scraper.find_image_urls()
    data_scraper.save_images(image_links)


if __name__ == "__main__":
    search_keys = get_search_keys("searchterms.txt")
    logger.info(f"Found {len(search_keys)} search keys: {search_keys}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(scraper, search_keys)
    sys.exit()
