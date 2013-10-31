#!/usr/bin/python

"""Homework 8: GUIs

Author: Jessica Hamrick <jhamrick@berkeley.edu>

Instructions
------------

Using Traits and TraitsUI create a GUI application that consists of
a search box, a text display, an image display, and a series of
buttons. The application will accept search strings in the search box
and then run an internet image search. The first returned image from
the search will be downloaded, the image url displayed in the text
display field, and the actual image displayed in the image display
field.

The buttons will provide the user interface to run the image search as
well as perform manipulations on the image currently stored in the
display (for example, blurring or rotation). Provide at least three
unique (and interesting) image manipulation functions.

Tips: Feel free to use an image search (or, include support for
multiple different searches). Yahoo has a convenient search
module. There is also freedom in how you display the image, but
matplotlib is recommended.

"""

try:
    import enthought.traits.api as tr
    import enthought.traits.ui.api as ui
except:
    import traits.api as tr
    import traitsui.api as ui

import urllib2
import simplejson
import tempfile
from PIL import Image, ImageEnhance
from mpl_figure_editor import MPLFigureEditor
from matplotlib.figure import Figure


class ImageEditor(tr.HasTraits):

    # the search query
    tags = tr.Str
    run = tr.Button("Run query")

    # the retrieved url
    url = tr.Str

    # the retrieved image
    figure = tr.Instance(Figure, ())

    # image manipulations
    reset = tr.Button
    blur = tr.Button
    sharpen = tr.Button
    decolor = tr.Button
    color = tr.Button
    darken = tr.Button
    brighten = tr.Button

    def __init__(self):
        super(ImageEditor, self).__init__()
        self._orig_image = None
        self._image = None
        self._factor = 0.1

    def _show(self):
        """Update the matplotlib axes with the image stored in `self._image`.

        """
        if self._image:
            self.figure.axes[0].images = []
            self.figure.axes[0].imshow(self._image)
            self.figure.canvas.draw()

    def _figure_default(self):
        """Returns an empty figure with a single subplot as the default
        matplotlib editor region.

        """
        # Add a default figure and axes
        figure = Figure()
        figure.add_subplot(111)
        return figure

    def _run_fired(self):
        """When the 'Run Query' button is pressed, perform an image search for
        the given query. Download the image at the first URL, and
        display both the image and the URL.

        """

        # don't do anything if there's an empty string passed
        if self.tags == "":
            return

        # Set up the image search request
        quoted = urllib2.quote(self.tags)
        url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
               'v=1.0&q=%s' % quoted)
        request = urllib2.Request(url, None)

        # Load the response and process the JSON string
        handler = urllib2.urlopen(request)
        results = simplejson.load(handler)
        handler.close()

        # Extract the URL for the first image (that we can download)
        for result in results['responseData']['results']:
            self.url = result['url']

            # Download the image
            request = urllib2.Request(self.url, None)
            try:
                handler = urllib2.urlopen(request)
            except urllib2.HTTPError:
                # we couldn't download the image for some reason, so
                # we'll try the next one
                pass
            else:
                break

        if handler:
            imagestr = handler.read()
        else:
            self.url = "Sorry, there was an error processing your query."

        # Save it to a temporary file and load it as a PIL image
        with tempfile.NamedTemporaryFile() as fh:
            fh.write(imagestr)
            self._orig_image = Image.open(fh.name)

        # Copy the image to our working buffer
        self._image = self._orig_image.copy()

        # Show the image
        self._show()

    def _reset_fired(self):
        """Reset the displayed image to the original version that was
        downloaded.

        """
        if self._orig_image:
            self._image = self._orig_image.copy()
            self._show()

    def _blur_fired(self):
        """Blur the displayed image."""
        if self._image:
            enhancer = ImageEnhance.Sharpness(self._image)
            factor = 1. - self._factor
            print "Blur by factor of %.2f" % factor
            self._image = enhancer.enhance(factor)
            self._show()

    def _sharpen_fired(self):
        """Sharpen the displayed image."""
        if self._image:
            enhancer = ImageEnhance.Sharpness(self._image)
            factor = 1. + self._factor
            print "Sharpen by factor of %.2f" % factor
            self._image = enhancer.enhance(factor)
            self._show()

    def _decolor_fired(self):
        """Desaturate the displayed image."""
        if self._image:
            enhancer = ImageEnhance.Color(self._image)
            factor = 1. - self._factor
            print "Decolor by factor of %.2f" % factor
            self._image = enhancer.enhance(factor)
            self._show()

    def _color_fired(self):
        """Increase saturation of the displayed image."""
        if self._image:
            enhancer = ImageEnhance.Color(self._image)
            factor = 1. + self._factor
            print "Color by factor of %.2f" % factor
            self._image = enhancer.enhance(factor)
            self._show()

    def _darken_fired(self):
        """Darken the displayed image."""
        if self._image:
            enhancer = ImageEnhance.Brightness(self._image)
            factor = 1. - self._factor
            print "Darken by factor of %.2f" % factor
            self._image = enhancer.enhance(factor)
            self._show()

    def _brighten_fired(self):
        """Brighten the displayed image."""
        if self._image:
            enhancer = ImageEnhance.Brightness(self._image)
            factor = 1. + self._factor
            print "Brighten by factor of %.2f" % factor
            self._image = enhancer.enhance(factor)
            self._show()

    # specify the way the various traits objects should be displayed
    view = ui.View(
        ui.Group(

            # the search query
            ui.Group(
                ui.Item(
                    'tags',
                    show_label=True,
                    label="Query string"),
                ui.Item(
                    'run',
                    show_label=False),

                orientation='horizontal',
                label="Input",
                show_border=True,
                springy=True),

            # the image url
            ui.Group(
                ui.Item(
                    'url',
                    style='readonly',
                    show_label=False),
                label="Image URL",
                show_border=True,
                springy=True),

            # the matplotlib figure for displaying the image
            ui.Group(
                ui.Item(
                    'figure',
                    editor=MPLFigureEditor(),
                    style='custom',
                    show_label=False,
                    width=500,
                    height=500),
                label="Image Display",
                show_border=True),

            # buttons for image manipulations
            ui.Group(
                ui.Item('reset'),
                ui.Item('blur'),
                ui.Item('sharpen'),
                ui.Item('decolor'),
                ui.Item('color'),
                ui.Item('darken'),
                ui.Item('brighten'),

                orientation='horizontal',
                show_labels=False,
                label="Image Manipulation Options",
                show_border=True,
                springy=True),

            show_labels=True,
            orientation='vertical'
        ),

        title="Image Search",
    )

if __name__ == "__main__":
    # create the editor and display it
    editor = ImageEditor()
    editor.configure_traits()
