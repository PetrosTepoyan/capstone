import requests
from bs4 import BeautifulSoup
from ConcreteScrapers.Bars.BarsApartmentScraper import BarsApartmentScraper
from Protocols import ApartmentScrapingPipeline
from Services import ImageLoader
import logging
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# https://bars.am/en/properties/standard/apartment
class BarsApartmentScrapingPipeline(ApartmentScrapingPipeline):

    def __init__(self, base_url, storage, image_loader: ImageLoader):
        self.base_url = base_url
        self.page = 1
        self.storage = storage
        self.image_loader = image_loader

        self.__set_soup(base_url)
        super().__init__(BarsApartmentScraper)
        
        # Instantiate a WebDriver (e.g., Chrome)
        driver = webdriver.Chrome()

        # Navigate to the page
        driver.get(base_url)
        self.driver = driver
        
        links = self.get_apartment_links()
        self.first_ap_link_on_this_page = links[0]

    def __set_soup(self, url):
        # Send a GET request to the website
        response = requests.get(url)

        # Check if the page is empty or not found, and break the loop if so
        if response.status_code != 200 or not response.text.strip():
            print("Failed", response.status_code)

        # Parse the HTML content of the page with BeautifulSoup
        self.soup = BeautifulSoup(response.text, 'html.parser')
        
    def finish(self):
        self.driver.quit()

    def __get_current_page_index(self):
        v = int(self.soup.find(class_="active hidden-xs").get_text())
        print(v)
        return v

    def navigate_to_next_page(self):
        # Wait for the element to be clickable and then click it
        try:
            
            # Find the element with the class 'fa fa-angle-right'
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "fa-angle-right"))
            )
            element.click()
            sleep(2)
            # Wait and check if the page has been changed
            # WebDriverWait(self.driver, 10).until(
            #     lambda driver: self.__get_current_page_index() != current_page
            # )

            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
        except Exception as e:
            print(e)
            logging.error(e)
           
        links = self.get_apartment_links() 
        if links[0] == self.first_ap_link_on_this_page:
            logging.error("did not navigate to next page")
        else:
            self.first_ap_link_on_this_page = links[0]

    def scrape_apartment(self, apartment_url):
        # Create an instance of ApartmentScraper with the provided URL
        apartment_scraper: BarsApartmentScraper = self.apartment_scraper(apartment_url)

        # Call the scrape method of the ApartmentScraper
        apartment_scraper.scrape()
        apartment_data = apartment_scraper.values()

        # Store or process the scraped data as needed
        self.storage.append(apartment_data)
        
        # download images
        images_links = apartment_scraper.images_links()
        if self.image_loader:
            self.image_loader.download_images(
                links = images_links,
                source = BarsApartmentScraper.source_identifier(),
                apartment_id = apartment_scraper.id
            )

    def get_apartment_links(self, page_url=None):
        if page_url is None:
            page_url = self.base_url

        # Find all 'a' elements with the specific class
        a_elements = self.soup.find_all('a', class_='wrapper-image')

        # Iterate over the found 'a' elements and navigate to their links
        links = []
        for a_element in a_elements:
            link = a_element.get('href')
            links.append(link)

        return links