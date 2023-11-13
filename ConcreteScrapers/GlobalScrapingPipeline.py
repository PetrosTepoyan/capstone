import concurrent.futures
from Protocols import ApartmentScrapingPipeline
from logging import Logger

class GlobalScrapingPipeline:
    
    def __init__(self, pipelines: list[ApartmentScrapingPipeline], logger: Logger):
        self.pipelines: list[ApartmentScrapingPipeline] = pipelines
        self.logger = logger
    
    def run_pipeline(self, pipeline):
        # Get apartments for the current page
        links = pipeline.get_apartment_links()
        
        # Scrape
        for link in links:
            pipeline.scrape_apartment(link)
            
        # Navigate to next apartment
        pipeline.navigate_to_next_page()
    
    
    def run(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_pipeline, pipeline) for pipeline in self.pipelines]
            
            # Wait for all futures to complete
            concurrent.futures.wait(futures)