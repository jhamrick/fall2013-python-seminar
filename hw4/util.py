import numpy as np


def weighted_sample(weights, size, axis=-1, rso=None):
    if rso is None:
        rso = np.random
    axes = range(len(weights.shape))
    if axis < 0:
        axis = len(axes) + axis
    newaxes = axes[:axis] + axes[axis+1:] + [axis]
    newweights = np.transpose(weights, newaxes)
    randshape = list(newweights.shape[:-1]) + [size, 1]
    rand = rso.rand(*randshape)
    bins = rand >= np.cumsum(newweights, axis=-1)[..., None, :]
    idx = np.sum(bins, axis=-1)
    return idx
