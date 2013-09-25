import matplotlib.pyplot as plt
import sys
import matplotlib.patches as mpatches
import numpy as np

class Brusher(object):

    def __init__(self, data, colors):
        """Initialize the brusher plots.

        Parameters
        ----------
        data : pandas.DataFrame
            Each column should represent a differen dimension of the
            data. The figure will have NxN subplots where N is the
            number of columns/dimensions.

        colors : numpy.ndarray
           The colors corresponding to each row in `data`.

        """

        # save the data and corresponding coclors
        self.data = data
        self.colors = colors

        # create the figure and axes
        self.ndim = len(self.data.columns)
        self.fig, self.axes = plt.subplots(self.ndim, self.ndim)

        # initialize instance variables
        self.loc0 = None
        self.loc1 = None
        self.xy0 = None
        self.xy1 = None
        self.ax0 = None
        self.rect = None

        # dictionaries to store the axis data and keys
        self.axis_dict = {}
        self.axis_data = {}

        for x, xstat in enumerate(self.data.columns):
            for y, ystat in enumerate(self.data.columns):

                # get the axis, and save the column names that
                # correspond to it
                ax = self.axes[y, x]
                self.axis_dict[str(ax)] = (xstat, ystat)
                # plot the data and save it for later in axis_data
                self.axis_data[x, y]= ax.scatter(
                    self.data[xstat], self.data[ystat])

                # set the axis limits iand ticks
                ax.set_xlim(self.data[xstat].min(), self.data[xstat].max())
                ax.set_ylim(self.data[ystat].min(), self.data[ystat].max())
                ax.xaxis.set_ticks([])
                ax.yaxis.set_ticks([])

                # plot a label on the diagonal plots
                if xstat == ystat:
                    ax.text(0.1, 0.85, xstat, transform=ax.transAxes)

        # set the colors of the data
        self.update_colors()

        # set the figure size
        self.fig.set_figwidth(10)
        self.fig.set_figheight(10)

        # draw
        self.fig.show()
        self.flush()

        # register mpl events (and save the ids, in case we want them later)
        self.cids = {}
        self.cids['button_press_event'] = self.fig.canvas.mpl_connect(
            'button_press_event', self.press)
        self.cids['button_release_event'] = self.fig.canvas.mpl_connect(
            'button_release_event', self.release)
        self.cids['key_press_event'] = self.fig.canvas.mpl_connect(
            'key_press_event', self.clear)

    def flush(self):
        """Flush standard out and draw the canvas."""
        sys.stdout.flush()
        self.fig.canvas.draw()

    def reset(self):
        """Reset the selection."""

        # remove the rectangle
        if self.rect:
            self.rect.remove()
            self.rect = None

        # update the points back to their original colors
        self.update_colors()

        # reset instance variables
        self.loc0 = None
        self.xy0 = None
        self.ax0 = None
        self.loc1 = None
        self.xy1 = None

    def press(self, event):
        """Handle a matplotlib mouse button press event."""

        # if there's already a selection, don't do anything
        if self.xy0:
            return

        # save the global mouse location, the axis coordinates, and
        # the axis object
        self.loc0 = (event.x, event.y)
        self.xy0 = (event.xdata, event.ydata)
        self.ax0 = event.inaxes

        # create a new rectangle patch and add it to the axis
        self.rect = mpatches.Rectangle(self.xy0, 0, 0, color='k', alpha=0.1)
        self.ax0.add_patch(self.rect)

        self.flush()

    def release(self, event):
        """Handle a matplotlib mouse button release event."""

        # if there's already a selection, don't do anything
        if self.xy1:
            return

        # save the global mojse location and axis coordinates
        self.loc1 = (event.x, event.y)
        self.xy1 = (event.xdata, event.ydata)

        # if the axes we started in aren't the same as the axes we're
        # in now, the user made an invalid selection
        if self.ax0 != event.inaxes:
            print "Warning: invalid selection"

        else:
            # figure out the area of the selection, and if it's really
            # small, then just return without doing anything because
            # it was probably an accidental click
            width = self.xy1[0] - self.xy0[0]
            height = self.xy1[1] - self.xy0[1]
            area = np.abs(width * height)
            if area < 0.001:
                self.reset()

            else:
                # update the width and height of our rectangle
                self.rect.set_width(width)
                self.rect.set_height(height)
                # pick out the points we want to highlight
                self.pick_points()

        self.flush()

    def clear(self, event):
        """Handle a matplotlib 'd' keypress, which clears the selection, if
        the mouse is inside the selection.

        """
        # maker sure the key pressed was d
        if event.key != "d":
            return

        # determine if the mouse was inside the selection
        xy = np.array([self.loc0, self.loc1]).T
        xmin = xy[0].min()
        xmax = xy[0].max()
        ymin = xy[1].min()
        ymax = xy[1].max()
        inregion = (
            (event.x > xmin) and
            (event.x < xmax) and
            (event.y > ymin) and
            (event.y < ymax)
        )

        # if it was in the selection, then reset it
        if inregion:
            self.reset()

    def pick_points(self):
        """Choose the points that are in the selection and update their
        colors.

        """

        # get the bounds of the selection
        xy = np.array([self.xy0, self.xy1]).T
        xmin = xy[0].min()
        xmax = xy[0].max()
        ymin = xy[1].min()
        ymax = xy[1].max()

        # get the data corresponding to the subplot we've made the
        # selection in
        xstat, ystat = self.axis_dict[str(self.ax0)]
        xdata = np.asarray(self.data[xstat])
        ydata = np.asarray(self.data[ystat])

        # determine which points to pick
        pick = ((xdata > xmin) &
                (xdata < xmax) &
                (ydata > ymin) &
                (ydata < ymax))

        # update the colors
        self.update_colors(pick=pick)

    def update_colors(self, pick=None):
        """Update the colors of the points in all the subplots, optionally
        setting some of the points to gray.

        Parameters
        ----------
        pick : boolean numpy.ndarray
            Where `False`, points will be set to have a gray color.

        """

        # update the color array
        colors = self.colors.copy()
        if pick is not None:
            colors[~pick] = (0, 0, 0, 0.1)

        # set the colors for each axis
        for (x, y), data in self.axis_data.iteritems():
            data.set_color(colors)
