import csv
from Storage import Storage

class CSVStorage(Storage):
    
    fieldnames = ["source", "id", "price", "facilities", "location", "area", "room", "floor", "storeys"]
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.initialize()

    def initialize(self):
        # Initialize the CSV file and write the header if the file doesn't exist
        with open(self.file_path, mode='a+', newline='') as file:
            file.seek(0)
            if not file.read(1):
                # File is empty, write the header
                writer = csv.DictWriter(file, fieldnames = self.fieldnames)
                writer.writeheader()
                
    def save_image(self, image, image_name):
        with open(image_name, 'wb') as f:
            f.write(image)

    def append(self, data_dict):
        # Append data in the CSV file
        with open(self.file_path, mode='a+', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writerow(data_dict)

    def path(self):
        return self.file_path
