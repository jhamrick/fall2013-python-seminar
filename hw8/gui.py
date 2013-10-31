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
from PIL import Image
from mpl_figure_editor import MPLFigureEditor
from matplotlib.figure import Figure


class Container(tr.HasTraits):
    tags = tr.Str
    run = tr.Button("Run query")
    url = tr.Str
    figure = tr.Instance(Figure, ())

    refresh = tr.Button
    blur = tr.Button
    sharpen = tr.Button
    smooth = tr.Button
    edge = tr.Button
    contrast = tr.Button
    color = tr.Button
    decolor = tr.Button
    brighten = tr.Button
    darken = tr.Button

    def _figure_default(self):
        # Add a default figure and axes
        figure = Figure()
        figure.add_subplot(111)
        return figure

    def _run_fired(self):
        # Set up the image search request
        quoted = urllib2.quote(self.tags)
        url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
               'v=1.0&q=%s' % quoted)
        request = urllib2.Request(url, None)

        # Load the response and process the JSON string
        handler = urllib2.urlopen(request)
        results = simplejson.load(handler)
        handler.close()

        # Extract the URL for the first image
        self.url = results['responseData']['results'][0]['url']

        # Download the image
        image_request = urllib2.Request(self.url, None)
        handler = urllib2.urlopen(image_request)
        imagestr = handler.read()

        # Save it to a temporary file and load it as a PIL image
        with tempfile.NamedTemporaryFile() as fh:
            fh.write(imagestr)
            image = Image.open(fh.name)

        # Update the matplotlib axes with the new image
        self.figure.axes[0].images = []
        self.figure.axes[0].imshow(image)
        self.figure.canvas.draw()

    view = ui.View(
        ui.Group(

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

            ui.Group(
                ui.Item(
                    'url',
                    style='readonly',
                    show_label=False),
                label="Image URL",
                show_border=True,
                springy=True),

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

            ui.Group(
                ui.Item('refresh'),
                ui.Item('blur'),
                ui.Item('sharpen'),
                ui.Item('smooth'),
                ui.Item('edge'),
                ui.Item('contrast'),
                ui.Item('color'),
                ui.Item('decolor'),
                ui.Item('brighten'),
                ui.Item('darken'),

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

container = Container()
container.configure_traits()
