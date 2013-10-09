import xmlrpclib
import numpy as np
from PIL import Image
import StringIO


def decode(image):
    strio = StringIO.StringIO()
    Image.fromarray(image).save(strio, format="jpeg")
    strio.seek(0)
    imstr = strio.read()
    strio.close()
    return xmlrpclib.Binary(imstr)


def encode(binary):
    strio = StringIO.StringIO(binary.data)
    image = Image.open(strio)
    image = np.asarray(image).copy()
    strio.close()
    return image
