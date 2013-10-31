# Homework 8: GUIs

Jessica Hamrick  
jhamrick@berkeley.edu

All of the code for this week is in the file `image_editor.py`, which
can be run from the command line. It displays a GUI using `traits`,
which allows you to search for and download an image via Google Image
Search, and subsequently edit that image. The modifications you can
perform are:

* Reset image to the original downloaded version
* Blur/sharpen
* Decolor/color
* Darken/brighten

Because there can sometimes be weirdness in remote HTTP queries,
sometimes an image can't be downloaded. In this case, the app will
attempt to get the second result, then the third, and so forth, until
it finds an image it can actually download.

The matplotlib figure is displayed via the code in
`mpl_figure_editor.py`, which was downloaded from the
[Enthought docs](http://code.enthought.com/projects/traits/docs/html/_static/mpl_figure_editor.py).
