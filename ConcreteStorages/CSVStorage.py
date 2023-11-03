import os
import csv
from Protocols.Storage import Storage
import threading

class CSVStorage(Storage):
    
    fieldnames = ["source", "id", "price", "facilities", "location", "area", "room", "floor", "storeys"]
    
    def __init__(self, file_path, images_path):
        self.file_path = file_path
        self.images_path = images_path
        self.initialize()
        self.threadLock = threading.Lock()

    def initialize(self):
        # Initialize the CSV file and write the header if the file doesn't exist
        with open(self.file_path, mode='a+', newline='') as file:
            file.seek(0)
            if not file.read(1):
                # File is empty, write the header
                writer = csv.DictWriter(file, fieldnames = self.fieldnames)
                writer.writeheader()
                
    def save_image(self, image, image_name):
        
        dir_path = os.path.dirname(self.images_path + image_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        with open(self.images_path + image_name, 'wb') as f:
            f.write(image)

    def append(self, data_dict):
        # Append data in the CSV file
        with open(self.file_path, mode='a+', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            self.threadLock.acquire()
            writer.writerow(data_dict)
            self.threadLock.release()

    def path(self):
        return self.file_path
