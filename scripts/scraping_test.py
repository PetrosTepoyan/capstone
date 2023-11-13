import sys
import logging
sys.path.append("..")

logging.basicConfig(filename = 'scraping.log', level = logging.INFO)
logger = logging.getLogger("main")
logger.info("This is a test message")

# MyRealty
from ConcreteScrapers.MyRealty.MyRealtyScrapingPipeline import MyRealtyScrapingPipeline

# Storage
from ConcreteStorages import CSVStorage

# Services
from Services import ImageLoader

storage = CSVStorage(
    file_path = "data/myrealty_apartments.csv",
    images_path = "../images/",
    logger = logger
)
storage.initialize()

image_loader = ImageLoader(
    storage,
    logger = logger
)

my_realty_scraper_pipeline = MyRealtyScrapingPipeline(
    "https://myrealty.am/en/apartments-for-sale/7784", 
    storage,
    image_loader = image_loader,
    logger = logger
)

links = my_realty_scraper_pipeline.get_apartment_links()
for link in links:
    my_realty_scraper_pipeline.scrape_apartment(link)