from io import BytesIO
import base64
from PIL import Image as PilImage
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from base64 import b64decode
import re
def convert_to_image(b64_str):
    try:
        image64 = b64_str.split(';base64,')[1]
        type64 = b64_str.split('data:image/')[1] \
                        .split(';base64,')[0]
    except IndexError:
        raise Exception('Wrong type of base64 image.')
    

    missing_padding = len(image64) % 4
    if missing_padding:
        image64 += b'='* (4 - missing_padding)
    image = BytesIO(base64.b64decode(image64))
    #image = BytesIO(b64decode(re.sub("data:image/jpeg;base64", '', b64_str)))
    new_image = Image()
    new_image = CoreImage(image, ext=type64)
    #with open("test.jpeg", 'wb') as f:
    #    f.write(b64decode(re.sub("data:image/jpeg;base64,", '', b64_str)))
    return new_image