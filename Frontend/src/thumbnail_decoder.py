import base64
import requests
from io import BytesIO
from PIL import Image

def thumbnail_decoder(image_data):
    """
    Decodes and converts the image data from base64 to an Image object.
    Args:
        image_data (str): The base64-encoded image data.
    Returns:
        PIL.Image.Image: The decoded image as a PIL Image object.
    """
    try:
        image_bytes = base64.b64decode(image_data)
        try:
            image = Image.open(BytesIO(image_bytes)).convert('RGB')
        except:
            image = Image.open(BytesIO(image_bytes)).convert('RGBA')
        return image
    except Exception as e:
        # Handle any exceptions that might occur during decoding
        raise ValueError(f"Error decoding image data: {e}")
    
    
def image_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        return image
    except:
        pass