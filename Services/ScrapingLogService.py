import pandas as pd
import threading

class ScrapingLogService:
    """
    A service for logging the results of web scraping operations.

    Attributes:
    path (str): The file path for the CSV log.
    log_df (DataFrame): A pandas DataFrame to hold log data.
    flash_interval (int): Counter for saving the DataFrame to CSV.
    lock (threading.Lock): A lock for thread-safe operations.
    """

    
    def __init__(self, path):
        """
        Initialize the ScrapingLogService with a path for the log file.

        Args:
        path (str): The file path for the CSV log.
        """
        
        self.path = path
        try:
            self.log_df = pd.read_csv(path, index_col=0)
        except:
            self.log_df = pd.DataFrame(columns=[
                "source",
                "webpage",
                "success",
                "error",
                "skipped"
            ])
        self.flash_interval = 0
        self.lock = threading.Lock()
        
    def did_scrape(self, webpage):
        """
        Check if a webpage has been successfully scraped before.

        Args:
        webpage (str): The URL of the webpage to check.

        Returns:
        bool: True if the webpage was successfully scraped, False otherwise.
        """
        with self.lock:
            # Check if the webpage exists in the log and if it was successfully scraped
            predicate = self.log_df['webpage'] == webpage
            same_webpage = self.log_df[predicate]
            if not same_webpage.empty:
                return True
            else:
                return False
        
    def start(self, source, webpage):
        """
        Log the start of a scraping operation for a webpage.

        Args:
        source (str): The source identifier of the scraping operation.
        webpage (str): The URL of the webpage being scraped.
        """
        new_row = pd.DataFrame({
            "source": [source],
            "webpage": [webpage],
            "success": [None],
            "error": [None],
            "skipped": [None]
        })
        
        with self.lock:
            self.log_df = pd.concat([self.log_df, new_row], ignore_index=True)
        
    def success(self, source, webpage):
        """
        Log the success of a scraping operation.

        Args:
        source (str): The source identifier of the scraping operation.
        webpage (str): The URL of the successfully scraped webpage.
        """
        with self.lock:
            self.log_df.loc[(self.log_df['webpage'] == webpage), 'success'] = True
            self.__increment_and_save()
        
    def error(self, source, webpage, error):
        """
        Log an error in a scraping operation.

        Args:
        source (str): The source identifier of the scraping operation.
        webpage (str): The URL of the webpage where the error occurred.
        error (str): The error message.
        """
        with self.lock:
            self.log_df.loc[(self.log_df['webpage'] == webpage), ['success', 'error']] = [False, error]
            self.__increment_and_save()

    def skipped(self, source, webpage):
        """
        Log a skipped scraping operation.

        Args:
        source (str): The source identifier of the scraping operation.
        webpage (str): The URL of the skipped webpage.
        """
        new_row = pd.DataFrame({
            "source": [source],
            "webpage": [webpage],
            "success": [None],
            "error": [None],
            "skipped": [True]
        })
        
        with self.lock:
            self.log_df = pd.concat([self.log_df, new_row], ignore_index=True)

    def __increment_and_save(self):
        """
        Increment the save counter and save the log if necessary.
        """
        self.flash_interval += 1
        if self.flash_interval > 0:
            self.flash_interval = 0
            self.save()
        
    def save(self):
        """
        Save the current state of the log to a CSV file.
        """
        self.log_df.to_csv(self.path)
