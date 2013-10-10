# Homework 5

Author: Jessica Hamrick  
Email: jhamrick@berkeley.edu

## Part 1

The image processing server provides five lossless operations:

1. `invert` -- invert the colors of an image
2. `flip_vertical` -- flip an image vertically (i.e., across the
   x-axis)
3. `flip_horizontal` -- flip an image horizontally (i.e., across the
   y-axis)
4. `rotate_counterclockwise` -- rotate an image 90 degrees
   counterclockwise
5. `rotate_clockwise` -- rotate an image 90 degrees clockwise

The server can be run from the command line using
`image_manipulation_server.py`:

```
$ python image_manipulation_server.py
Started XML-RPC server at 127.0.0.1:5021
```

The notebook `client.ipynb` demonstrates use of the client. It asks
the server to perform several operations, and also requests
documentation about how each method works.

## Part 2

The notebook `sound_processing.ipynb` performs an analysis of the
given sound files, and attempts to identify which notes are present in
each of the audio signals. It relies on a series of helper functions
in `sound.py`, which load the audio file, perform various
computations, and generate various plots.

Plots of the musical scale vs. average power have been saved in the
`notes/` directory; they illustrate the power of each note. Notes are
identified as being a part of the audio file either if they have the
highest power, or if they have at least half the power of the
strongest note.
