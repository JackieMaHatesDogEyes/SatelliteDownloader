import requests

from io import BytesIO

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

from tempfile import NamedTemporaryFile

import os

class Projection:
    EQUIRECTANGULAR = 4326
    WEBMERCATOR = 3857

    SQUARE = 3857
    RECTANGULAR = 4326


def ArcGIS (z : int, x : int, y : int):
    return f"https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

def Google (z : int, x : int, y : int):
    return f"https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"

def OSM(z : int, x : int, y : int):
    return f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
def OpenStreetMap(z : int, x : int, y : int):
    return OSM(z, x , y)

class SatImage:
    def __init__(self, image: Image):
        self.Image = image

    def __str__(self):
        return f"SatImage Instance ({repr(self)})"

    def Export(self, name: str, extension='jpg', projection: int = 3857,  folder="."):
        # 3857 = Web Mercator (default)
        # 4326 = Equirectangular
        if projection == 4326:
            os.chdir(folder)
            img = NamedTemporaryFile("wb", suffix=".tif", dir=".", delete=False)
            self.Image.save(img, format='TIFF')
            
            img.flush()
            
            os.system(f"gdal_translate -a_srs EPSG:3857 -a_ullr -20037508 20037508 20037508 -20037508 {img.name} ./output.tif")
            os.system(f"gdalwarp -s_srs EPSG:3857 -t_srs EPSG:4326 output.tif intermediate.tif")
            img.close()
            os.remove(img.name)
            os.remove("output.tif")

            if "tif" not in extension or "tiff" not in extension:
                temp = Image.open("intermediate.tif")
                temp.save(f"{name}.{extension}")
                os.remove("intermediate.tif")
            else:
                os.replace("intermediate.tif", f"{name}.{extension}")
            

            os.chdir("../")
            

        elif projection == 3857:
            self.Image.save(f"{name}.{extension}")
        
        else:
            raise Exception(f"Invalid Projection (or not supported): {projection}")

    

    def Download(zoom : int, x : int, y : int, source = ArcGIS):

        
        try:
            url = source(zoom, x, y)


        except AttributeError:
            if isinstance(source, str):
                url = source
            else:
                raise Exception(f"Invalid source: '{source}'")

        headers = {
            'User-Agent': 'M'
        } # Bypass User Agent Limits
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Got error code: {response.status_code}")


        img = BytesIO()
        img.write(response.content)

        image = Image.open(img)

        return SatImage(image)

   


def GetWorld(zoom:int, source = ArcGIS):
    max_range = 2 ** zoom

    img_arr = [
        [] for _ in range(max_range)
    ]

    image_res = max_range * 256






    counter = 0

    for x in range(0, max_range):
        for y in range(0, max_range):
            img = SatImage.Download(zoom, x, y, source=source)
            img_arr[y].append(img.Image)
            print(f"Downloading Tile: {x}:{y}")
        counter += 1

    image = Image.new('RGB', (256 * len(img_arr), 256 * len(img_arr)))

    w_counter = 0
    h_counter = 0

    for h in img_arr:
        for w in h:
            image.paste(im=w, box=(w_counter, h_counter))
            w_counter += 256
        w_counter = 0
        h_counter += 256

    return SatImage(image)





        
