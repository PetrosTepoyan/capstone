import aiohttp
import asyncio

class ImageLoader:
    def __init__(self, storage):
        self.storage = storage
            
    async def download_image(self, session, url, source, apartment_id, index):
        async with session.get(url) as response:
            if response.status != 200:
                return

            extension = url.split(".")[-1]
            image_path = f"{source}/{apartment_id}/{index}.{extension}"
            bytes = await response.read()
            self.storage.save_image(bytes, image_path)

    async def __download_images(self, links, source, apartment_id):
        async with aiohttp.ClientSession() as session:
            tasks = [self.download_image(session, url, source, apartment_id, ind) for ind, url in enumerate(links)]
            await asyncio.gather(*tasks)

    def download_images(self, links, source, apartment_id):
        if asyncio.get_running_loop():
            asyncio.create_task(self.__download_images(links, source, apartment_id))
        else:
            asyncio.run(self.__download_images(links, source, apartment_id))