import pandas as pd
import threading

class ScrapingLogService:
    
    def __init__(self, path):
        self.path = path
        self.log_df = pd.DataFrame(columns=[
            "source",
            "webpage",
            "success",
            "error",
            "skipped"
        ])
        self.flash_interval = 0
        self.lock = threading.Lock()
        
    def start(self, source, webpage):
        
        if self.log_df[self.log_df['webpage'] == webpage].empty:
            new_row = pd.DataFrame({
                "source": [source],
                "webpage": [webpage],
                "success": [None],
                "error": [None],
                "skipped": [None]
            })
            
            with self.lock:
                self.log_df = pd.concat([self.log_df, new_row], ignore_index=True)
        else:
            self.skipped(
                source = source,
                webpage = webpage
            )
        
    def success(self, source, webpage):
        with self.lock:
            self.log_df.loc[(self.log_df['webpage'] == webpage), 'success'] = True
            self.__increment_and_save()
        
    def error(self, source, webpage, error):
        with self.lock:
            self.log_df.loc[(self.log_df['webpage'] == webpage), ['success', 'error']] = [False, error]
            self.__increment_and_save()

    def skipped(self, source, webpage):
        with self.lock:
            self.log_df.loc[(self.log_df['webpage'] == webpage), 'skipped'] = True
            self.__increment_and_save()

    def __increment_and_save(self):
        self.flash_interval += 1
        if self.flash_interval > 10:
            self.flash_interval = 0
            self.save()
        
    def save(self):
        self.log_df.to_csv(self.path)
