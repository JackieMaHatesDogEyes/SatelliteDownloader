import requests
import os
from io import BytesIO
from PIL import Image

class SatDownloader:
    def __init__(self):
        self.URL = "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{x}/{y}"

    def GetTile(self, name: str, zoom:int, x:int, y:int, fp=None):

        if x >= (2 ** zoom) or y >= (2 ** zoom):
            raise Exception("Invalid Zoom.")


        url = self.URL.replace("{z}", str(zoom)).replace("{x}", str(x)).replace("{y}", str(y))
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Got error code: {response.status_code}")

        image = response.content
        print(url)
        if not fp:
            with open(f"{name}.jpg", "wb") as file:
                file.write(image)
        else:
            fp.write(image)
            return fp

        

    def GetWorldAtZoom(self, zoom: int, folder:str = "out", filename="world", extension="jpg"):
        image_array = [
            [] for _ in range(2 ** zoom)
        ]

        max_zoom = 2 ** zoom

        final_image_res = (2 ** zoom) * 256 # resolution (256px x 256px)
        

        if not os.path.exists(folder):
            os.makedirs(folder)
        os.chdir(folder)

        
        counter = 0

        for x in range(0, max_zoom): # x

            for y in range(0, max_zoom):
                img = BytesIO()
                img = self.GetTile(f'worldx{y}y{x}', zoom, x, y, img)
                img = Image.open(img) 
                image_array[x].append(img)
                print(y)
            counter += 1

        image = Image.new('RGB', (256 * len(image_array), 256 * len(image_array)))

        width_counter = 0
        height_counter = 0
        for h in image_array:
            for w in h:
                image.paste(im=w, box=(width_counter, height_counter))
                width_counter += 256
            width_counter = 0
            height_counter += 256

        image.save(f"{filename}.{extension}")
        

        


