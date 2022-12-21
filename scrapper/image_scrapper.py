import logging
import os

import gridfs
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import requests
import io
from PIL import Image
import time
from Logging.Customlogger import class_customlogger
from db_connection.Databaseoperations import Mongodb_operations
from selenium.common.exceptions import NoSuchElementException
import pandas as pd


class scrapper:

    def __init__(self, db_operation_obj: Mongodb_operations):
        self.log = class_customlogger.custom_logger_fn(logger_name=__name__, logLevel=logging.DEBUG,
                                                       log_filename="imagescrapper.log")
        self.url = "https://images.google.com/"
        self.path = './chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=self.path, options=self.set_chrome_options())
        self.db_operation_obj = db_operation_obj

    def set_chrome_options(self):
        try:
            self.log.info("Setting the chrome options")
            # create an object of chrome class
            chrome_options = Options()
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("excludeSwitches", ["--disable - popup - blocking"])
            chrome_options.set_capability("pageLoadStrategy", "eager")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument('--incognito')
            # path of chrome driver
            # Creates a new instance of the chrome driver.
            # Starts the service and then creates new instance of chrome driver.
            # Controls the ChromeDriver and allows you to drive the browser.
            return chrome_options
        except Exception as e:
            self.log.exception(e)

    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def scroll_down(self):
        try:
            self.log.info("scrolling down")
            SCROLL_PAUSE_TIME = 1
            # Get scroll height
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # no more data is present to scroll down
                    break
                last_height = new_height
            try:
                show_more_results = '//*[@id="islmp"]/div/div/div/div/div[1]/div[2]/div[2]/input'
                end_of_page = '//*[@id="islmp"]/div/div/div/div/div[1]/div[2]/div[1]/div[2]/div[1]/div'
                if self.check_exists_by_xpath(show_more_results):
                    self.log.info("show more option present")
                    self.driver.find_element_by_xpath(show_more_results).click()
                    self.log.info("show more option clicked")
                    self.scroll_down()
                if self.check_exists_by_xpath(end_of_page):
                    self.log.info("Reached end of the page")
            except Exception as e:
                self.log.error(e)
            self.log.info("scrolled down")

        except Exception as e:
            self.log.exception(e)

    def scroll_up(self):
        try:
            self.driver.execute_script("window.scrollTo(0,0)")

        except Exception as e:
            self.log.error(e)

    def get_image_urls(self, num_images: int, pause=2):
        self.log.info("Executing the get urls method")
        image_url_set = set()

        try:
            # find the thumbnails in the search page
            thumbnails = self.driver.find_elements_by_class_name("Q4LuWd")
            self.log.info(f"Found {len(thumbnails)} number of thumbnails")
            for each_image in thumbnails:
                try:
                    # click on each thumbnail and get the bigger picture with good resolution.
                    each_image.click()
                    time.sleep(pause)
                except Exception as e:
                    self.log.error(e)
                big_image = self.driver.find_elements_by_class_name("n3VNCb")

                # append to the image url set if image has a http link in the image src:
                for image in big_image:
                    if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                        link = image.get_attribute('src')
                        image_url_set.add(link)
                        https_found = len(image_url_set)
                        self.log.info(f"Found {https_found} http link")
                if len(image_url_set) == num_images:
                    self.log.info(f"Found {len(image_url_set)} urls...search completed ")
                    self.log.info(f"Reached the max number of links specified")
                    break
            return image_url_set

        except Exception as e:
            self.log.error(e)

    def save_urls_to_excel(self, urls_set, keyword):
        try:
            self.log.info("Executing the save_urls_to_excel method")
            urls_links_df = pd.DataFrame(urls_set, columns=[keyword])
            if not os.path.exists("Output"):
                self.log.info("The output folder doesnt exists")
                self.log.info("Creating the output folder")
                os.mkdir("output")
            else:
                self.log.info("The output folder exists")

            wb_name = keyword + '_' + 'image_urls.xlsx'
            folder_path = '.\output\ ' + wb_name
            self.log.info(f"Saving the urls to excel-->{wb_name}")

            urls_links_df.to_excel(folder_path, sheet_name='image_urls', index=None)
        except Exception as e:
            self.log.error(e)

    def get_final_set_links(self, keyword, urls_set):

        links_present_in_db = []
        for i in self.db_operation_obj.db.fs.files.find({'search_string': keyword}, {'_id': 1}):
            links_present_in_db.extend(list(i.values()))

        common_links = set(urls_set).intersection(set(links_present_in_db))

        if len(common_links) > 0:
            self.log.info(f"{len(common_links)}:links are already present in db")
            self.log.info(f"These links are already present in db {common_links}")
            links_not_present_in_db = list(set(urls_set) - set(links_present_in_db)) + list(set(links_present_in_db) - set(urls_set))
            self.log.info(f"{len(links_not_present_in_db)}links are not present in db")
            self.log.info(f"These links are not present in db {links_not_present_in_db}")
            return links_not_present_in_db, len(common_links)
        else:
            links_not_present_in_db = urls_set
            self.log.info(f"{len(links_not_present_in_db)}: links are not present in db")
            self.log.info(f"These links are not present in db {links_not_present_in_db}")
        return links_not_present_in_db, len(common_links)

    def download_urls_to_folder(self, final_urls_set, len_common_links, keyword):
        self.log.info("Executing the download_urls_to_folder method")
        target_folder = './Output/' + keyword
        if not os.path.exists(target_folder):
            self.log.info(f"Target folder {target_folder} doesnt exists")
            os.mkdir(target_folder)
        else:
            self.log.info(f"Target folder {target_folder} already exists")
        count = len_common_links
        for each_url in final_urls_set:
            image_data = requests.get(each_url).content
            suffix = str(count + 1)
            image_name = keyword + suffix + ".jpg"
            f = open(os.path.join(target_folder, image_name), 'wb')
            f.write(image_data)
            self.log.info(f"Saved the {keyword + suffix} to {target_folder}")
            f.close()
            self.db_operation_obj.insert_data(target_folder, image_name, keyword, each_url)
            count += 1
        return f"downloaded the images to {target_folder}"

    def search_image_in_google(self, keyword, num_of_images=10):
        self.log.info("Executing the search_image_in_google method")
        try:
            self.driver.get(self.url)
            # self.driver.refresh()
            self.driver.maximize_window()
            try:
                search_box = self.driver.find_element_by_xpath(
                    '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
            except Exception as e:
                self.log.error(e)
            search_box.send_keys(keyword)
            self.log.info(f"searching for {keyword}...")
            search_box.send_keys(Keys.ENTER)
            self.scroll_down()
            self.scroll_up()
            urls_set = self.get_image_urls(num_of_images)
            self.save_urls_to_excel(urls_set, keyword)
            final_urls, len_common_links = self.get_final_set_links(keyword, urls_set)
            msg = self.download_urls_to_folder(final_urls, len_common_links, keyword)
            self.driver.quit()
            return msg
        except Exception as e:
            self.log.error(e)
