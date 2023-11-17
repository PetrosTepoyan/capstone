from ConcreteScrapers.GlobalScrapingPipeline import GlobalScrapingPipeline

# Bnakaran
from ConcreteScrapers.Bnakaran.BnakaranScrapingPipeline import BnakaranScrapingPipeline

# Bars
from ConcreteScrapers.Bars.BarsApartmentScrapingPipeline import BarsApartmentScrapingPipeline

# MyRealty
from ConcreteScrapers.MyRealty.MyRealtyScrapingPipeline import MyRealtyScrapingPipeline

# Storage
from ConcreteStorages import CSVStorage, ImageStorage

# Services
from Services import ImageLoader, ScrapingLogService

# Misc
import os
import logging
from bnakaran_sitemap_apartments import bnakaran_sitemap_apartments

scraping_folder = "scraping_results/"
# os.mkdir("scraping_results/")
logging.basicConfig(filename = scraping_folder + 'scraping.log', level = logging.INFO)

# Defining storages
image_storage = ImageStorage(
    images_path = scraping_folder + "images/",
    image_error_log_path = scraping_folder + "image_error_log.csv"
)

bnakaran_storage = CSVStorage(
    file_path = scraping_folder + "data/bnakaran_apartments.csv"
)
bnakaran_storage.initialize()

bars_storage = CSVStorage(
    file_path = scraping_folder + "data/bars_apartments.csv"
)
bars_storage.initialize()

myrealty_storage = CSVStorage(
    file_path = scraping_folder + "data/myrealty_apartments.csv"
)
myrealty_storage.initialize()

# Services
image_loader = ImageLoader(image_storage)
log_service = ScrapingLogService(
    path = scraping_folder + "scraping_log.csv"
)

# Defining pipelines
myrealty_scraper_pipeline = MyRealtyScrapingPipeline(
    "https://myrealty.am/en/apartments-for-sale/7784", 
    myrealty_storage,
    image_loader = image_loader
)
print("Initialized MyRealty")

bnakaran_scraper_pipeline = BnakaranScrapingPipeline(
    "https://www.bnakaran.com/en/listing?ctype=apartment&deal=sale&country=am&sort=relevance", 
    bnakaran_storage,
    image_loader
)
print("Initialized Bnakaran")

bars_scraper_pipeline = BarsApartmentScrapingPipeline(
    "https://bars.am/en/properties/standard/apartment", 
    bars_storage,
    image_loader
)
print("Initialized Bars")

print("Starting...")
global_scraping_pipeline = GlobalScrapingPipeline(
    pipelines = [
        bnakaran_scraper_pipeline, 
        bars_scraper_pipeline,
        myrealty_scraper_pipeline
    ],
    log_service = log_service
)

bnakaran_sitemap = bnakaran_sitemap_apartments()

global_scraping_pipeline.run(
    submit_overriding_future = (bnakaran_scraper_pipeline.scrape_links, bnakaran_sitemap)
)
