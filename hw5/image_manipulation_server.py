import os
import numpy as np
import StringIO
import xmlrpclib

from PIL import Image
from SimpleXMLRPCServer import SimpleXMLRPCServer


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


def serializable(func):
    """Helper decorator which encodes the input image as a numpy array,
    passes the encoded image to the function, and decodes the output
    back to a serialized format.

    """

    def code_image(self, data):
        image = decode(data)
        new_image = func(self, image)
        return encode(new_image)

    # ensure that the decorated function has the same name and
    # docstring as the original function
    code_image.__doc__ = func.__doc__ + """

    Parameters
    ----------
    image : xmlrpclib.Binary object

    Returns
    -------
    xmlrpclib.Binary object

    """
    code_image.__name__ = func.__name__
    return code_image


def save_images(func):
    """Helper decorator which saves the input and output images of a
    function.

    """

    # make the image directory if it does not exist
    if not os.path.exists("server_images"):
        os.makedirs("server_images")

    def save(self, image):
        # call the function
        new_image = func(self, image)
        # get the name of the function
        name = func.__name__
        # save the input and output images to disk
        Image.fromarray(image).save(
            "server_images/%s_in.jpg" % name)
        Image.fromarray(new_image).save(
            "server_images/%s_out.jpg" % name)
        return new_image

    # ensure that the decorated function has the same name and
    # docstring as the original function
    save.__doc__ = func.__doc__
    save.__name__ = func.__name__
    return save


class ImageManipulations(object):
    """A collection of lossless image manipulation methods. These include:

        * invert
        * flip_vertical
        * flip_horizontal
        * rotate_counterclockwise
        * rotate_clockwise

    """

    @serializable
    @save_images
    def invert(self, image):
        """Invert the colors of an image."""
        return 255 - image

    @serializable
    @save_images
    def flip_vertical(self, image):
        """Flip an image vertically (i.e., across the x-axis)."""
        return image[::-1]

    @serializable
    @save_images
    def flip_horizontal(self, image):
        """Flip an image horizontally (i.e., across the y-axis)."""
        return image[:, ::-1]

    @serializable
    @save_images
    def rotate_counterclockwise(self, image):
        """Rotate an image 90 degrees counterclockwise."""
        return image.swapaxes(0, 1)[::-1]

    @serializable
    @save_images
    def rotate_clockwise(self, image):
        """Rotate an image 90 degrees clockwise."""
        return image.swapaxes(0, 1)[:, ::-1]


class ImageManipulationServer(SimpleXMLRPCServer):
    """A simple subclass of SimpleXMLRPCServer that registers the
    appropriate image manipulation functions (see the
    ImageManipulations class).

    """

    def __init__(self, host="127.0.0.1", port=5021):
        SimpleXMLRPCServer.__init__(self, (host, port), allow_none=True)

        self.register_instance(ImageManipulations())
        self.register_multicall_functions()
        self.register_introspection_functions()

        print "Started XML-RPC server at %s:%d" % (host, port)


if __name__ == "__main__":
    # instantiate the server
    server = ImageManipulationServer()
    # start listening for requests
    server.serve_forever()
