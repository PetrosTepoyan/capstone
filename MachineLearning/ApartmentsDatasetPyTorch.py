import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

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
        
    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        try:
            image = Image.open(image_path)
        except:
            self.error_log[idx] = "cant load"
            return None
        
        if self.transform:
            image = self.transform(image)
        
        price = self.__get_price_from_image_path(image_path)
        return image, price
    
    def __get_price_from_image_path(self, image_path):
        components = image_path.split("/")
        source = components[2]
        ap_native_id = components[3]
        filtered_rows = self.df[(self.df["source"] == source) & (self.df["id"] == ap_native_id)]
        
        try:
            price = int(filtered_rows["price"])
        except:
            print(filtered_rows["price"])
            print(source, ap_native_id)
            return None
        return price
