import re
import requests
from bs4 import BeautifulSoup
from ConcreteScrapers.Bnakaran.BnakaranApartmentScraper import BnakaranApartmentScraper
from Protocols import ApartmentScrapingPipeline
from Services import ImageLoader
import logging
import threading

class BnakaranScrapingPipeline(ApartmentScrapingPipeline):

    def __init__(self, base_url, storage, image_loader: ImageLoader):
        self.base_url = base_url
        self.page = 1
        self.storage = storage
        self.image_loader = image_loader
        self.cached_links = set()
        self.lock = threading.Lock()

        self.__set_soup(base_url)
        super().__init__(BnakaranApartmentScraper)

    def __set_soup(self, url):
        response = requests.get(url)
        if response.status_code != 200 or not response.text.strip():
            logging.error(f"Failed to fetch the webpage. Status code: {response.status_code}")
            return

        self.soup = BeautifulSoup(response.text, 'html.parser')

    def navigate_to_next_page(self):
        self.page += 1
        self.__set_soup(f"{self.base_url}?page={self.page}")

    def scrape_apartment(self, apartment_url):
        with self.lock:
            if apartment_url not in self.cached_links:
                self.cached_links.add(apartment_url)
            else:
                logging.info(f"Bnakaran Skipping {apartment_url}")
                return False
        
        apartment_scraper = self.apartment_scraper(apartment_url)
        apartment_scraper.scrape()
        apartment_data = apartment_scraper.values()

        self.storage.append(apartment_data)

        images_links = apartment_scraper.images_links()
        if self.image_loader:
            self.image_loader.download_images(
                links=images_links,
                source=BnakaranApartmentScraper.source_identifier(),
                apartment_id=apartment_data.get('id', 'unknown')  # Assuming you have an 'id' field in your details
            )
        return True

    def get_apartment_links(self):
        # Find all <a> tags with hrefs that end in -d followed by some numbers
        apartment_links = self.soup.find_all('a', href = re.compile(r"-d\d+$"))

        # Extract hrefs from the links
        apartment_hrefs = set([link.get('href') for link in apartment_links])
        links = [self.get_base_link() + ap_link for ap_link in apartment_hrefs]
        return links

    def get_base_link(self) -> str:
        return "https://www.bnakaran.com"