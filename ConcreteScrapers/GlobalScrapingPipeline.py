import concurrent.futures
from Protocols import ApartmentScrapingPipeline
import logging
from Services import ScrapingLogService
import traceback

class GlobalScrapingPipeline:
    """
    Manages and executes multiple apartment scraping pipelines concurrently.
    """
    
    def __init__(self, pipelines: list[ApartmentScrapingPipeline], log_service: ScrapingLogService):
        """
        Initializes the GlobalScrapingPipeline with a list of scraping pipelines and a log service.

        :param pipelines: List of ApartmentScrapingPipeline instances to manage.
        :param log_service: Instance of ScrapingLogService for logging.
        """
        self.pipelines: list[ApartmentScrapingPipeline] = pipelines
        self.log_service: ScrapingLogService = log_service
        self.scraped_hashes = set()
    
    def run_pipeline(self, pipeline: ApartmentScrapingPipeline):
        """
        Runs a single scraping pipeline, iterating through apartment links and managing logging.

        :param pipeline: An ApartmentScrapingPipeline instance to run.
        """
        source = pipeline.apartment_scraper.source_identifier()
        
        # Get apartments for the current page
        links = pipeline.get_apartment_links()
        tupled_list = tuple(links)
        list_hash = hash(tupled_list)
        
        skipped_links_count = 0
        for link in links:
            
            if self.log_service.did_scrape(link):
                skipped_links_count += 1
                continue
            
            self.log_service.start(
                source = source,
                webpage = link
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
        
        if skipped_links_count != 0:
            logging.info(source + f" | Skipped {len(links)}/{skipped_links_count} links from this page")
        
        if len(links) != 0:
            # Navigate to next page
            try:
                pipeline.navigate_to_next_page()
            except:
                logging.critical(source + " | failed to navigate")
                return
                
            logging.info(source + f"| Navigated to page {pipeline.page}")
            self.run_pipeline(pipeline)
            
        else:
            logging.critical(source + " | no more links")
    
    def run(self):
        """
        Executes all scraping pipelines concurrently.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.run_pipeline, pipeline) for pipeline in self.pipelines
            ]
            # Wait for all futures to complete
            concurrent.futures.wait(futures) 
            
            # Check for errors in each future
            for future in futures:
                error = future.exception()
                if error is not None:
                    # Handle or log the error here
                    print(f"Error in future: {error}")
                    logging.error(error)
                    traceback.print_exc()