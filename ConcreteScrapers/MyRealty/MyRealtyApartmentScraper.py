import os
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from ApartmentScraper import ApartmentScraper

class MyRealtyApartmentScraper(ApartmentScraper):
    
    def __init__(self, webpage):
        
        # Send a GET request to the website
        response = requests.get(webpage)

        # Check if the page is empty or not found, and break the loop if so
        if response.status_code != 200 or not response.text.strip():
            print("Failed", response.status_code)

        # Parse the HTML content of the page with BeautifulSoup
        self.soup = BeautifulSoup(response.text, 'html.parser')
        
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
            self.__scrape_images()
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
    
    def __scrape_id(self) -> bool:
        # Find the div with the specific class and extract the ID
        id_div = self.soup.find('div', class_='item-view-id')
        id_text = id_div.get_text(strip=True)  # Get the text content of the div
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
            price_element_text = price_element.get_text(strip=True)
            price_text_stripped = price_element_text.split("/")[0]
            price_text_stripped = price_text_stripped.replace(",", "")
            price = int(price_text_stripped)
            self.price = price
            
    def __scrape_location(self):
        # Find the div with the specific id
        div_tag = self.soup.find('div', id='yandex_map_item_view')

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
        
    def __scrape_images(self):
        # Extract image URLs
        # Find img elements with the specific classes
        img_elements = self.soup.find_all('img', class_=['owl-lazy', 'lazy-loaded'])

        # Extract the src attribute of the img elements
        img_urls = set([img['data-src'] for img in img_elements if 'data-src' in img.attrs])

        async def download_image(session, url, image_index):
            async with session.get(url) as response:
                # Check if the request was successful
                if response.status != 200:
                    return

                apartment_images_path = f'images/{self.id}'
                # Create a directory to save the images if it doesn't exist
                if not os.path.exists(apartment_images_path):
                    os.makedirs(apartment_images_path)

                # Save the image to the local file system
                extension = url.split(".")[-1]
                file_name = os.path.join(apartment_images_path, f"{image_index}.{extension}")
                with open(file_name, 'wb') as f:
                    f.write(await response.read())
#                 print(f"Downloaded {url}")

        async def main():
            async with aiohttp.ClientSession() as session:
                tasks = [download_image(session, url, ind) for ind, url in enumerate(img_urls)]
                await asyncio.gather(*tasks)
#             print(f"All images for ID {self.id} have been downloaded.")

        # Check if there is a running event loop
        if asyncio.get_running_loop():
            # If there is a running event loop, use create_task to schedule the coroutine
            asyncio.create_task(main())
        else:
            # If there is no running event loop, use asyncio.run() to execute the coroutine
            asyncio.run(main())
            