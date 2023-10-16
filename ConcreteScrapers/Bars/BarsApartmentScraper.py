import os
import re
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from ApartmentScraper import ApartmentScraper

class BarsApartmentScraper(ApartmentScraper):
    
    def __init__(self, webpage):
        
        response = requests.get(webpage)

        if response.status_code != 200 or not response.text.strip():
            print("Failed", response.status_code)

        self.soup = BeautifulSoup(response.text, 'html.parser')
        
    @staticmethod
    def source_identifier():
        return "bars"
        
    # must through some errors
    def scrape(self):
        
        self.id = self.__get_id()
        self.price = self.__get_price()
        self.facilities = self.__get_facilities()
        self.address = self.__get_address()
        self.area = self.__get_quick_data("Apartment area (sq/m):", float)
        self.rooms = self.__get_quick_data("Number of rooms:", int)
        self.floor = self.__get_quick_data("Floor:", int)
        self.storeys = self.__get_quick_data("Floors:", int)
        
        self.bedrooms = self.__get_quick_data("Number of bedrooms:", int)
        self.bathrooms = self.__get_quick_data("Number of bathrooms:", int)
        self.ceiling_height = self.__get_quick_data("Ceiling height (m):", float) 
        self.building_type = self.__get_quick_data("Building Type:", str)
        self.condition = self.__get_quick_data("Condition:", str)
        
        
    def values(self):
        return {
            "source" : BarsApartmentScraper.source_identifier(),
            "id": self.id,
            "price" : self.price,
            "facilities" : self.facilities,
            "location" : self.address,
            "area" : self.area,
            "rooms" : self.rooms,
            "floor" : self.floor,
            "storeys" : self.storeys,
            
            "bedrooms" : self.bedrooms,
            "bathrooms" : self.bathrooms,
            "ceiling_height" : self.ceiling_height,
            "building_type" : self.building_type,
            "condition" : self.condition
        }
        
        
    def __get_quick_data(self, label: str, type_) -> any:
        quick_data_tag = self.soup.find('strong', text=f'{label}').parent
        quick_data_text = ''.join(quick_data_tag.stripped_strings).replace(f'{label}', '').strip()
        return type_(quick_data_text)
    
    def __get_id(self) -> str:
        # Use a regex pattern to find the div containing the desired text
        div_tag = self.soup.find('div', string=re.compile("Code: (\d+)"))

        # If the tag is found, extract the value using the regex
        if div_tag:
            match = re.search("Code: (\d+)", div_tag.text)
            if match:
                value = match.group(1)
                return value
        else:
            return None
        
    def __get_address(self) -> str:
        # Find the div tag with the specific id "listing-address-label"
        div_tag = self.soup.find('div', id="listing-address-label")

        # If the tag is found, extract the text content after the icon
        if div_tag:
            address = div_tag.text.replace('<i class="fa fa-map-marker"></i>', '').strip()
            return address
        else:
            return None
        
    def __get_price(self) -> int:
        # Find the div tag with the specific class "price for-sale-2"
        div_tag = self.soup.find('div', class_="price for-sale-2")

        # If the tag is found, extract the text content after the icon
        if div_tag:
            price = div_tag.text.replace('<i class="fa fa-usd"></i>', '').strip().replace(",", "")
            return int(price)
        else:
            return None
        
    def __get_facilities(self) -> list:
        amenities = [item.span.text for item in self.soup.findAll('li', class_='amenities-item')]
        return amenities
    
    def __get_image_links(self) -> list:
        image_links = [img['src'] for img in self.soup.findAll('img')]
        final_links = []
        for link in image_links:
            if "uploads/listing-pics/" in link and "_" not in link:
                final_links.append(link)
        return final_links