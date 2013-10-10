import xmlrpclib
import numpy as np
from PIL import Image
import StringIO


def encode(image):
    """Encode an image to XML-RPC base-64 encoding.

    Parameters
    ----------
    image : np.ndarray

    Returns
    -------
    xmlrpclib.Binary instance

    """
    # save the image into a string buffer
    strio = StringIO.StringIO()
    Image.fromarray(image).save(strio, format="jpeg")
    # read out the string from the buffer
    strio.seek(0)
    imstr = strio.read()
    strio.close()
    # create a binary object from the string
    return xmlrpclib.Binary(imstr)


def decode(binary):
    """Decode an image from XML-RPC base-64 encoding to an array.

    Parameters
    ----------
    binary : xmlrpclib.Binary instance

    Returns
    -------
    numpy.ndarray

    """
    # create a string buffer from the string (binary data)
    strio = StringIO.StringIO(binary.data)
    # create a PIL image from that string and then convert it to a
    # numpy array
    image = Image.open(strio)
    image = np.asarray(image).copy()
    strio.close()
    return image
