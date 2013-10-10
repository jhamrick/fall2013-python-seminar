from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlimage import encode, decode
from PIL import Image
import os


def serializable(func):
    def code_image(self, data):
        image = encode(data)
        new_image = func(self, image)
        return decode(new_image)
    code_image.__doc__ = func.__doc__
    code_image.__name__ = func.__name__
    return code_image


def save_images(func):
    def save(self, image):
        name = func.__name__
        new_image = func(self, image)
        if not os.path.exists("server_images"):
            os.makedirs("server_images")
        Image.fromarray(image).save(
            "server_images/%s_in.jpg" % name)
        Image.fromarray(new_image).save(
            "server_images/%s_out.jpg" % name)
        return new_image
    save.__doc__ = func.__doc__
    save.__name__ = func.__name__
    return save


class ImageManipulations(object):

    @serializable
    @save_images
    def invert(self, image):
        return 255 - image

    @serializable
    @save_images
    def flip_vertical(self, image):
        return image[::-1]

    @serializable
    @save_images
    def flip_horizontal(self, image):
        return image[:, ::-1]

    @serializable
    @save_images
    def rotate_counterclockwise(self, image):
        return image.swapaxes(0, 1)[::-1]

    @serializable
    @save_images
    def rotate_clockwise(self, image):
        return image.swapaxes(0, 1)[:, ::-1]


class ImageManipulationServer(SimpleXMLRPCServer):

    def __init__(self, host="127.0.0.1", port=5021):
        SimpleXMLRPCServer.__init__(self, (host, port), allow_none=True)

        self.register_instance(ImageManipulations())
        self.register_multicall_functions()
        self.register_introspection_functions()

        print "Started XML-RPC server at %s:%d" % (host, port)


if __name__ == "__main__":
    # TODO: do some argument parsing for the host and port
    server = ImageManipulationServer()
    server.serve_forever()
