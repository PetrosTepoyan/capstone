from abc import ABC, abstractmethod

class ApartmentScraper(ABC):
    @abstractmethod
    def scrape(self):
        """
        Abstract method for scraping the current page of an individual apartment.
        Subclasses must implement this method.
        """
        pass

    @abstractmethod
    def values(self):
        """
        Abstract method for returning a dictionary with keys and values scraped from the apartment page.
        Subclasses must implement this method.
        """
        pass
