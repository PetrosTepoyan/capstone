import pandas as pd

class ScrapingLogService:
    
    def __init__(self, path):
        self.path = path
        self.log_df = pd.DataFrame(columns = [
            "source",
            "webpage",
            "success",
            "error"
        ])
        
    def success(self, source, webpage):
        new_row = pd.DataFrame({
            "source" : [source],
            "webpage" : [webpage],
            "success" : [True],
            "error" : [None]
        })
        self.log_df = pd.concat([self.log_df, new_row], ignore_index = True)
        
    def error(self, source, webpage, error):
        new_row = pd.DataFrame({
            "source" : [source],
            "webpage" : [webpage],
            "success" : [False],
            "error" : [error]
        })
        self.log_df = pd.concat([self.log_df, new_row], ignore_index = True)
        
    def save(self):
        self.log_df.to_csv(self.path)