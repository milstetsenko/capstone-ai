from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager       

import time
import os
import requests
import io
from PIL import Image
import logging.config
import logging
from typing import Tuple, List


logging.config.fileConfig("logging.conf")
log = logging.getLogger("scraper")


class DataScraper:
    def __init__(self, image_path: str,
            search_key: str = "", folder_key: str = "", number_of_images: int = 300,
                 headless: bool = True, min_resolution: Tuple[int, int] = (300, 300),
                 max_resolution: Tuple[int, int] = (1920, 1080)):
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
            driver.get("https://www.google.com")
        except Exception as e:
            log.error(e)
            exit(1)

        self.driver = driver
        self.search_key = search_key
        self.folder_key = folder_key
        self.number_of_images = number_of_images
        self.image_path = image_path
        self.url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947"%(search_key)
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        
    def find_image_urls(self) -> List[str]:
        log.info("Scraping Google Images for links")
        image_urls = []
        count = 0
        missed_count = 0
        self.driver.get(self.url)
        time.sleep(3)
        idx = 1
        while self.number_of_images > count:
            try:
                #find and click image
                imgurl = self.driver.find_element_by_xpath(f'//*[@id="islrg"]/div[1]/div[{str(idx)}]/a[1]/div[1]/img')
                imgurl.click()
                missed_count = 0 
            except Exception as e:
                log.error(e)
                missed_count = missed_count + 1
                if missed_count > 10:
                    log.info("No more photos")
                    break
                 
            try:
                #select image from the popup
                time.sleep(1)
                class_names = ["n3VNCb"]
                images = [self.driver.find_elements_by_class_name(class_name) for class_name in class_names
                          if len(self.driver.find_elements_by_class_name(class_name)) != 0][0]
                for image in images:
                    #only download images that starts with http
                    src_link = image.get_attribute("src")
                    if(("http" in  src_link) and (not "encrypted" in src_link)):
                        log.info(f"Found {count} links")
                        image_urls.append(src_link)
                        count += 1
                        break
            except Exception as e:
                log.warning("Unable to access the link")
                log.warning(e)
                
            try:
                #scroll page to load next image
                if count % 3 == 0:
                    self.driver.execute_script("window.scrollTo(0, "+str(idx*60)+");")
                element = self.driver.find_element_by_class_name("mye4qd")
                element.click()
                log.info("Scrolling to the next page")
                time.sleep(3)
            except Exception as e:
                print(e)
                time.sleep(1)
            idx += 1
        self.driver.quit()
        log.info(f"Finished searching for links, found {count}")
        return image_urls

    def save_images(self, image_urls: List[str]) -> None:
        log.info("Starting to download the images")
        for idx, image_url in enumerate(image_urls):
            try:
                log.info(f"Downloading image url: {image_url}")
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url, timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        try:
                            filename = f"{self.folder_key}_{idx}.{image_from_web.format.lower()}"
                            image_path = os.path.join(self.image_path, filename)
                            image_from_web.save(image_path)
                            log.info(f"Image saved at: {image_path}")
                        except OSError:
                            rgb_im = image_from_web.convert('RGB')
                            rgb_im.save(image_path)
                        image_resolution = image_from_web.size
                        if image_resolution is not None:
                            if image_resolution[0] < self.min_resolution[0] \
                                    or image_resolution[1] < self.min_resolution[1] \
                                    or image_resolution[0] > self.max_resolution[0] \
                                    or image_resolution[1] > self.max_resolution[1]:
                                image_from_web.close()
                                log.info(f"{image_url} didn't meet resolution requirements, stop download process")
                                os.remove(image_path)

                        image_from_web.close()
            except Exception as e:
                log.error(f"Failed to download image {e}", e)
                pass
        log.info("Finished downloading")
