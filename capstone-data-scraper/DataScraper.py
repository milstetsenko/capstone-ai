from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager       
from datetime import datetime as dt
import time
import os
import requests
import io
from PIL import Image
import logging.config
import logging
from typing import Tuple, Set


logging.config.fileConfig("logging.conf")
log = logging.getLogger("scraper")


class DataScraper:
    def __init__(self, image_path: str,
            search_key: str = "", folder_key: str = "", max_images: int = 500,
            headless: bool = True, min_resolution: Tuple[int, int] = (256, 256), delay: float = 1):
        image_path = os.path.join(image_path, folder_key)
        if not os.path.exists(image_path):
            os.makedirs(image_path)
            log.info(f"Image path not found. Created a new folder {image_path}")
        try:
            #try going to www.google.com
            options = webdriver.ChromeOptions()
            options.add_argument("--window-size=1920,1080")
            if headless:
                options.add_argument('--headless')
            driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                      options=options)
        except Exception as e:
            log.error(f"Unable to initialize Chrome driver: {e}")
            exit(1)

        self.driver = driver
        self.search_key = search_key
        self.folder_key = folder_key
        # to account for wrong sizes and formats
        self.max_images = max_images
        self.image_path = image_path
        self.url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947"%(search_key)
        self.min_resolution = min_resolution
        self.delay = delay

    def scroll_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(self.delay)

    def find_image_urls(self) -> Set[str]:
        self.driver.get(self.url)

        image_urls = set()
        skips = 0
        while len(image_urls) + skips < self.max_images:
            self.scroll_down()
            thumbnails = self.driver.find_elements(By.CLASS_NAME, "Q4LuWd")

            for img in thumbnails[len(image_urls) + skips:self.max_images]:
                try:
                    img.click()
                    time.sleep(self.delay)
                except:
                    continue

                images = self.driver.find_elements(By.CLASS_NAME, "n3VNCb")
                for image in images:
                    if image.get_attribute('src') in image_urls:
                        self.max_images += 1
                        skips += 1
                        break

                    if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                        image_urls.add(image.get_attribute('src'))
                        print(f"Found {len(image_urls)}")

        return image_urls


    # Return % of saved images 
    def save_images(self, image_urls: Set[str], image_format: str = "JPEG", verbose: bool = False) -> float:
        print(f"Trying to save images to {self.image_path}")
        if not os.path.exists(self.image_path):
            os.makedirs(self.image_path)
            print(f"Created {self.image_path}")
        download_count = 0
        for i, url in enumerate(image_urls):
            try:
                time = dt.now()
                curr_time = time.strftime('%H:%M:%S')
                #Content of the image will be a url
                img_content = requests.get(url).content
                #Get the bytes IO of the image
                img_file = io.BytesIO(img_content)
                #Stores the file in memory and convert to image file using Pillow
                img = Image.open(img_file)

                if img.size[0] < self.min_resolution[0] or img.size[1] < self.min_resolution[1]:
                    continue
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                file_pth = os.path.join(self.image_path, self.folder_key) + f"_{i}.jpeg"

                with open(file_pth, 'wb') as file:
                    img.save(file, image_format)
                    download_count += 1
                if verbose == True:
                   print(f'The image: {file_pth} downloaded successfully at {curr_time}.')
            except Exception as e:
                print(f'Unable to download image from Google Photos due to\n: {str(e)}')
        return 100*download_count/len(image_urls)
