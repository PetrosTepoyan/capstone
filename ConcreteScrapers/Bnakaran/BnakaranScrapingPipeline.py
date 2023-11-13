import requests
from bs4 import BeautifulSoup
from ConcreteScrapers.Bnakaran.BnakaranApartmentScraper import BnakaranApartmentScraper
from Protocols import ApartmentScrapingPipeline
from Services import ImageLoader
from logging import Logger

class BnakaranScrapingPipeline(ApartmentScrapingPipeline):

    def __init__(self, base_url, storage, image_loader: ImageLoader, logger: Logger):
        self.base_url = base_url
        self.page = 1
        self.storage = storage
        self.image_loader = image_loader
        self.logger = logger

        self.__set_soup(base_url)
        super().__init__(BnakaranApartmentScraper, logger)

    def __set_soup(self, url):
        response = requests.get(url)
        if response.status_code != 200 or not response.text.strip():
            self.logger.error(f"Failed to fetch the webpage. Status code: {response.status_code}")
            return

        self.soup = BeautifulSoup(response.text, 'html.parser')

    def navigate_to_next_page(self):
        self.page += 1
        self.__set_soup(f"{self.base_url}?page={self.page}")

    def scrape_apartment(self, apartment_url):
        apartment_scraper = self.apartment_scraper(apartment_url)
        apartment_scraper.scrape()
        apartment_data = apartment_scraper.values()

        self.storage.append(apartment_data)

        images_links = apartment_scraper.images_links()
        self.image_loader.download_images(
            links=images_links,
            source=BnakaranApartmentScraper.source_identifier(),
            apartment_id=apartment_data.get('id', 'unknown')  # Assuming you have an 'id' field in your details
        )

    def get_apartment_links(self, page_url=None):
        if page_url is None:
            page_url = self.base_url

        # Assuming that the links to apartments are contained within 'a' tags with a certain class
        a_elements = self.soup.find_all('a', class_='apartment-link-class')

        links = [a.get('href') for a in a_elements]
        return links
