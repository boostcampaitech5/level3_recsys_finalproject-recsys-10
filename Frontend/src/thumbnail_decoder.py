import base64
from io import BytesIO
from PIL import Image

def thumbnail_decoder(image_data):
    image_bytes = base64.b64decode(image_data)
    try:
        image = Image.open(BytesIO(image_bytes)).convert('RGB')
    except:
        image = Image.open(BytesIO(image_bytes)).convert('RGBA')
    return image