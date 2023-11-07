import requests
from bs4 import BeautifulSoup
from Protocols import ApartmentScraper
from logging import Logger

class MyRealtyApartmentScraper(ApartmentScraper):
    
    def __init__(self, webpage: str, logger: Logger):
        
        # Send a GET request to the website
        response = requests.get(webpage)

        # Check if the page is empty or not found, and break the loop if so
        if response.status_code != 200 or not response.text.strip():
            print("Failed", response.status_code)

        # Parse the HTML content of the page with BeautifulSoup
        self.soup = BeautifulSoup(response.text, 'html.parser')
        self.logger = logger
        
    @staticmethod
    def source_identifier():
        return "myrealty"
    
    # must through some errors
    def scrape(self):
        success = self.__scrape_id()
        
        if success:
            self.__scrape_price()
            self.__scrape_facilities()
            self.__scrape_location()
            self.__scrape_misc()
        else:
            raise Exception
            
    def values(self):
        return {
            "source" : MyRealtyApartmentScraper.source_identifier(),
            "id": self.id,
            "price" : self.price,
            "facilities" : self.facilities,
            "location" : self.address,
            "area" : self.area,
            "room" : self.room,
            "floor" : self.floor,
            "storeys" : self.storeys
        }
        # need to scrape bathroom count, building type, ceiling height, condition
        
    def images_links(self) -> list[str]:
        # Extract image URLs
        # Find img elements with the specific classes
        img_elements = self.soup.find_all('img', class_=['owl-lazy', 'lazy-loaded'])

        # Extract the src attribute of the img elements
        img_urls: list[str] = list(set([img['data-src'] for img in img_elements if 'data-src' in img.attrs]))
        return img_urls
    
    def __scrape_id(self) -> bool:
        # Find the div with the specific class and extract the ID
        id_div = self.soup.find('div', class_ = 'item-view-id')
        id_text = id_div.get_text(strip = True)  # Get the text content of the div
        id_number = id_text.split()[-1]  # Split the text and get the last part, which is the ID number
        
        if id_number is None:
            return False
        else:
            self.id = id_number
            return True
        
    def __scrape_facilities(self):
        facilities = [li.find('label').get_text() for li in self.soup.find_all('li', class_='col-sm-6 col-lg-4 col-xl-3 mb-1')]
        self.facilities = facilities

    def __scrape_price(self):
        price_element = self.soup.find('div', class_='pl-0')
        if price_element:
            price_element_text = price_element.get_text(strip = True)
            price_text_stripped = price_element_text.split("/")[0]
            price_text_stripped = price_text_stripped.replace(",", "")
            price = int(price_text_stripped)
            self.price = price
            
    def __scrape_location(self):
        # Find the div with the specific id
        div_tag = self.soup.find('div', id = 'yandex_map_item_view')

        # Extract the latitude and longitude from the data-lat and data-lng attributes
        latitude = div_tag['data-lat']
        longitude = div_tag['data-lng']
        self.latitude = latitude
        self.longitude = longitude
        
        address_div = self.soup.find('div', class_='col-auto item-view-address d-none d-xl-block mr-0')

        # Extract the text within the div element
        address = address_div.get_text(strip=True)
        self.address = address

        
    def __scrape_misc(self):
        # Find the parent div with the specific class
        parent_div = self.soup.find('div', class_='col-12 d-flex justify-content-between justify-content-sm-start item-view-price-params')

        # Extract the area, room, floor, and storeys
        area = parent_div.find('div', class_='pl-0').find('span').text
        room = parent_div.find_all('div')[1].find('span').text
        floor_storeys = parent_div.find_all('div')[2].find('span').text
        floor, storeys = floor_storeys.split('/')

        self.area = area
        self.room = room
        self.floor = floor
        self.storeys = storeys