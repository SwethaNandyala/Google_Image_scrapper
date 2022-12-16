import logging
import os

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
        self.image_url_list = []
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

    def get_image_urls(self,keyword):
        thumbnails = self.driver.find_elements_by_class_name("Q4LuWd")
        print(len(thumbnails))
        for each_icon in thumbnails:
            each_icon.click()
            time.sleep(2)
            image_source = self.driver.find_elements_by_class_name("n3VNCb")
            for image in image_source:
                image_src = image.get_attribute("src")
                if image_src and "http" in image_src:
                    self.image_url_list.append(image_src)
        col_name=keyword
        links_df = pd.DataFrame(self.image_url_list, columns=[col_name])

        if not os.path.exists("Output"):
            self.log.info("The output folder doesnt exists")
            self.log.info("Creating the output folder")
            os.mkdir("output")
        else:
            self.log.info("The output folder exists")

        self.log.info("saving the links to an excel")
        links_df.to_excel('.\output\image_urls.xlsx', sheet_name="image_urls", index=None)

        return self.image_url_list

    def search_image_in_google(self, keyword):
        self.driver.get(self.url)
        # self.driver.refresh()
        self.driver.maximize_window()
        search_box = self.driver.find_element_by_xpath(
            '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)
        self.scroll_down()
        self.scroll_up()
        self.get_image_urls(keyword)



    def download_image_from_urls(self):
        pass


db_operation = Mongodb_operations(db_name="google_images")
db_operation.get_or_create_collection("image_collection")
sc = scrapper(db_operation)
sc.search_image_in_google("cat")
