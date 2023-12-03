import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch

class ApartmentsDatasetPyTorch(Dataset):
    def __init__(self, data_dir, images_dir, transform=None):
        """
        Args:
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        
        self.data_dir = data_dir
        self.images_dir = images_dir
        self.transform = transform
        self.image_paths = []
        self.df = pd.read_csv(data_dir)
        self.df.id = self.df.id.astype(str)
        
        for subdir, dirs, files in os.walk(images_dir):
            for file in files:
                if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".jpeg"):
                    img_path = os.path.join(subdir, file)
                    if os.path.getsize(img_path) > 0:
                        self.image_paths.append(img_path)
                    
        self.error_log = {}
        
    def tabular_data_size(self):
        return len(self.df.columns) - 4 # id, source, price, coordinates
        
    def __len__(self):
        return len(self.image_paths)

    # Introducing is_valid, because sometimes there is a mismatch between 
    # the images and their tabular data. 
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        components = image_path.split("/")
        source = components[-3]
        ap_native_id = components[-2]
        
        try:
            image = Image.open(image_path)
            if self.transform:
                image = self.transform(image)
            is_valid = True
            
        except Exception as e:
            self.error_log[idx] = f"Error loading image: {e}"
            return (None, None, None, False)

        price = self.__get_price_from_image_path(image_path)
        if price is None:
            self.error_log[idx] = "Price not found"
            return (None, None, None, False)

        # Assuming 'data' represents some other data you want to return
        data = self.df[(self.df["source"] == source) & (self.df["id"] == ap_native_id)]
        data = data.drop(columns = ["id", "source", "price", "coordinates"]).to_numpy()
        data = torch.from_numpy(data)
        data = data.to(torch.float32)
        return (image, data, price, is_valid)

    
    def __get_price_from_image_path(self, image_path):
        components = image_path.split("/")
        source = components[-3]
        ap_native_id = components[-2]
        filtered_rows = self.df[(self.df["source"] == source) & (self.df["id"] == ap_native_id)]
        try:
            price = int(filtered_rows["price"])
        except:
            # print(source, ap_native_id)
            return None
        price = torch.tensor(price)
        return price
