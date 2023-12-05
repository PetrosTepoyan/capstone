import aiohttp
import asyncio
import logging
from ConcreteStorages import ImageStorage

class ImageLoader:
    """
    Service that is responsible for downloading images
    """
    
    def __init__(self, storage: ImageStorage):
        """
        Initialize the ImageLoader with an ImageStorage instance.

        Args:
        storage (ImageStorage): An instance of ImageStorage to handle downloaded images.
        """
        self.storage = storage
            
            
    async def download_image(self, session, url, source, apartment_id, index):
        """
        Asynchronously download an image from a given URL and save it using the ImageStorage.

        Args:
        session (aiohttp.ClientSession): The session object for making HTTP requests.
        url (str): The URL of the image to download.
        source (str): The source identifier for logging.
        apartment_id (str): The identifier of the apartment for which the image is being downloaded.
        index (int): The index of the image in the sequence of apartment images.

        Returns:
        None: This method does not return anything but saves the image or logs errors.
        """
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return

                extension = url.split(".")[-1]
                image_path = f"{source}/{apartment_id}/{index}.{extension}"
                bytes = await response.read()
                self.storage.save_image(bytes, image_path)
        except Exception as e:
            self.storage.image_error_log(
                source = source, 
                url = url,
                apartment_id = apartment_id,
                index = index,
                error = e
            )
            logging.error(f"Can't download image {apartment_id} {index}")
            

    async def __download_images(self, links, source, apartment_id):
        """
        Asynchronously download a list of images for a specific apartment.

        Args:
        links (list): A list of URLs for the images to download.
        source (str): The source identifier for logging.
        apartment_id (str): The identifier of the apartment for which the images are being downloaded.

        Returns:
        None: This method does not return anything but orchestrates the downloading of images.
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.download_image(session, url, source, apartment_id, ind) for ind, url in enumerate(links)]
            await asyncio.gather(*tasks)


    def download_images(self, links, source, apartment_id):
        """
        Download images for a specific apartment, either asynchronously or synchronously based on the context.

        Args:
        links (list): A list of URLs for the images to download.
        source (str): The source identifier for logging.
        apartment_id (str): The identifier of the apartment for which the images are being downloaded.

        Returns:
        None: This method does not return anything but triggers the image downloading process.
        """
        try:
            if asyncio.get_running_loop():
                asyncio.create_task(self.__download_images(links, source, apartment_id))
            else:
                asyncio.run(self.__download_images(links, source, apartment_id))
        except:
            # Meaning running in a sync context, need to force running in an event loop
            asyncio.run(self.__download_images(links, source, apartment_id))