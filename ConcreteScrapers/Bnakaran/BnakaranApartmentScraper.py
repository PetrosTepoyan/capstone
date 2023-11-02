import requests
from bs4 import BeautifulSoup

class BnakaranApartmentScraper:
    
    def __init__(self, webpage: str):
        # Send a GET request to the website
        response = requests.get(webpage)
        
        # Check if the page is empty or not found, and break the loop if so
        if response.status_code != 200 or not response.text.strip():
            print("Failed to fetch the webpage. Status code:", response.status_code)
            return
        
        # Parse the HTML content of the page with BeautifulSoup
        self.soup = BeautifulSoup(response.content, 'html.parser')
    
    @staticmethod
    def source_identifier():
        return "bnakaran"
    
    def scrape(self):
        self.__scrape_features()
        self.__scrape_images()
        self.__scrape_location()
        self.__scrape_details()
        self.__scrape_room_details()
        self.__scrape_additional_features()
        
    def values(self):
        return {
            "source" : BnakaranApartmentScraper.source_identifier(),
            "area": self.area,
            "storeys": self.storeys,
            "rooms": self.rooms,
            "images": self.images,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "details": self.details,
            "room_details": self.room_details,
            "additional_features": self.additional_features
        }
        
    def __scrape_features(self):
        for li in self.soup.select('ul.property-main-features > li'):
            key = li.get_text(strip=True).split(':')[0].strip().lower()
            value = li.find('span').get_text(strip=True)
            if key == 'area':
                self.area = ''.join(filter(str.isdigit, value))
            elif key == 'storey':
                self.storeys = ''.join(filter(str.isdigit, value.split('/')[0]))
            elif key == 'rooms':
                self.rooms = ''.join(filter(str.isdigit, value))
    
    def __scrape_images(self):
        self.images = [a['href'] for a in self.soup.find_all('a', class_='item', href=True)]
    
    def __scrape_location(self):
        yandex_map_div = self.soup.find('div', class_='yandex-map')
        if yandex_map_div:
            self.latitude = yandex_map_div.get('data-y')
            self.longitude = yandex_map_div.get('data-x')
        else:
            print("Yandex map element not found on the page.")
    
    def __scrape_details(self):
        self.details = {}
        property_features = self.soup.find('ul', class_='property-features').find_all('li', recursive=False)
        for feature in property_features:
            parts = feature.get_text(strip=True).split(':')
            if len(parts) >= 2:
                key, value = parts[0].strip(), parts[1].strip()
                self.details[key] = value
                
    def __scrape_utilities(self):
        utilities_list = self.soup.find('ul', class_='property-features margin-top-0')
        self.utilities = {}
        
        if utilities_list:
            utilities_items = utilities_list.find_all('li', recursive=False)
            for utility in utilities_items:
                utility_text = utility.get_text(strip=True)
                if ':' in utility_text:
                    utility_key = utility_text.split(':')[0].strip()
                    utility_value = utility.find('span').get_text(strip=True) if utility.find('span') else "Not specified"
                    
                    if utility_key:
                        self.utilities[utility_key] = utility_value
                else:
                    print(f"Unexpected format for utility item: {utility_text}")
        else:
            print("Utilities information is not available.")

    
    def __scrape_room_details(self):
        features_lists = self.soup.find_all('ul', class_='property-features')
        if len(features_lists) > 1:
            room_features_list = features_lists[1].find_all('li', recursive=False)
            self.room_details = {}
            for feature_item in room_features_list:
                parts = feature_item.get_text(strip=True).split(':')
                if len(parts) >= 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    self.room_details[key] = value
        else:
            print("The expected room details section was not found")
    
    def __scrape_additional_features(self):
        features_list = self.soup.find('ul', class_='property-features checkboxes margin-top-0')
        if features_list:
            feature_items = features_list.find_all('li', recursive=False)
            self.additional_features = [feature.get_text(strip=True) for feature in feature_items]
        else:
            print("Additional features information is not available.")
