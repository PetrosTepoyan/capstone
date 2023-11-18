import pandas as pd
import threading

class ScrapingLogService:
    
    def __init__(self, path):
        self.path = path
        self.log_df = pd.DataFrame(columns = [
            "source",
            "webpage",
            "success",
            "error"
        ])
        self.flash_interval = 10
        self.lock = threading.Lock()
        
    def success(self, source, webpage):
        new_row = pd.DataFrame({
            "source" : [source],
            "webpage" : [webpage],
            "success" : [True],
            "error" : [None]
        })
        with self.lock:
            self.log_df = pd.concat([self.log_df, new_row], ignore_index = True)
            self.__increment_and_save()
        
    def error(self, source, webpage, error):
        new_row = pd.DataFrame({
            "source" : [source],
            "webpage" : [webpage],
            "success" : [False],
            "error" : [error]
        })
        with self.lock:
            self.log_df = pd.concat([self.log_df, new_row], ignore_index = True)
            self.__increment_and_save()
        
    def __increment_and_save(self):
        self.flash_interval += 1
        if self.flash_interval > 10:
            self.save()
        
    def save(self):
        self.log_df.to_csv(self.path)