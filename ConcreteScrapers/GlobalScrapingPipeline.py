import concurrent.futures
from Protocols import ApartmentScrapingPipeline
import logging
from Services import ScrapingLogService

class GlobalScrapingPipeline:
    
    def __init__(self, pipelines: list[ApartmentScrapingPipeline], log_service: ScrapingLogService):
        self.pipelines: list[ApartmentScrapingPipeline] = pipelines
        self.log_service: ScrapingLogService = log_service
    
    def run_pipeline(self, pipeline: ApartmentScrapingPipeline):
        # Get apartments for the current page
        links = pipeline.get_apartment_links()
        
        # Scrape
        for link in links:
            source = pipeline.apartment_scraper.source_identifier()
            
            self.log_service.start(
                source = source,
                link = link
            )
            
            try:
                pipeline.scrape_apartment(link)
                self.log_service.success(
                    source = source,
                    webpage = link
                )
            except Exception as e:
                self.log_service.error(
                    source = source,
                    webpage = link,
                    error = str(e)
                )
        
        if len(links) != 0:
            # Navigate to next page
            pipeline.navigate_to_next_page()
            self.run_pipeline(pipeline)
            logging.info(pipeline.apartment_scraper.source_identifier() + "| Navigated to next page")
        else:
            logging.critical(pipeline.apartment_scraper.source_identifier() + " | no more links")
    
    def run(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.run_pipeline, pipeline) for pipeline in self.pipelines
            ]
            # Wait for all futures to complete
            concurrent.futures.wait(futures) 