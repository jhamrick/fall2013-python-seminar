"""Image processing and feature extraction

To compute features for training, run:

`python image_processing.py`.

This script assumes there is a directory called `50_categories`, which
contains subdirectories named by category, and then within each
subdirectory the actual images.

Running this script from the command line will load the images,
perform some basic preprocessing (equalizing, scaling, etc.), and
compute features. It will then save the feature array to a file called
`image_dataset.npy`, and the categories to a file called
`image_categories.npy` (these are both numpy files, and can be loaded
by calling `np.load`).

"""

# built-in
import os
import sys
from glob import glob
# external
import numpy as np
import skimage.exposure
import skimage.feature
import skimage.filter
import skimage.filter.rank
import skimage.io
import skimage.morphology


def load_image(img_path, n=400):
    """Load an image from file, and perform minimal processing on it to
    prepare it for feature extraction.

    Specifically, this function does the following operations:

        1) Load image
        2) Convert to RGB if grayscale
        3) Equalize histograms
        4) Denoise
        5) Resize

    Parameters
    ----------
    img_path : string
        The path to the image
    n : int (optional)
        The size to scale the largest dimension to

    Returns
    -------
    img : numpy.ndarray

    """
    # load the image from file
    img = skimage.io.imread(img_path).astype('f8')
    # make sure it has three channels
    if img.ndim == 2:
        img = img[:, :, None] * np.ones(img.shape + (3,))

    # equalize histograms
    img = skimage.exposure.equalize_hist(img)
    # reduce noise
    img = skimage.filter.denoise_bilateral(img, 3, 0.1)

    # scale largest dimension to be of size n
    shape = img.shape[:2]
    scale = float(n) / max(shape)
    img = skimage.transform.rescale(img, scale)
    shape = img.shape[:2]

    return img


def extract_features(img):
    """Extract a vector of features from an image. The feature vector is
    flat, but has the following components:

        1) Mean of R, G, and B channels
        2) Covariance between R, G, and B channels
        3) Summary statistics of image entropy

    Parameters
    ----------
    img : numpy.ndarray
        The image to extract features from.

    Returns
    -------
    feature_vec : numpy.ndarray
        One-dimensional numpy array of features

    """
    RGB = img.reshape((-1, 3)).T

    # mean of each channel
    mean = np.mean(RGB, axis=1)
    # median of each channel
    median = np.median(RGB, axis=1)
    # covariance between channels
    cov = np.cov(RGB).ravel()
    # (normalized) entropy of the grayscale image
    entropy = skimage.filter.rank.entropy(
        np.mean(img, axis=-1).astype('uint16'),
        skimage.morphology.disk(5))
    entropy = entropy / float(img.size)
    entropy_sum = np.sum(entropy)
    entropy_mean = np.mean(entropy)
    entropy_var = np.var(entropy)

    # concatenate all the features together
    feature_vec = np.concatenate(
        [mean, median, cov, [entropy_sum, entropy_mean, entropy_var]])

    return feature_vec


def get_image_categories(images):
    """Get the true categories of a set of paths to images, based on the
    directory they are located in.

    The paths should have the form:
        path/to/image/category/image.jpg

    Where the image filename is the last item in the path, and the
    directory (category name) is the second to last item in the path.

    Parameters
    ----------
    images : list
        List of paths to images

    Returns
    -------
    categories : numpy.ndarray
        An array of integers in order of the images, corresponding to
        each image's category
    category_map : list
        A list of category names. The category integers in
        `categories` are indices into this list.

    """
    get_category = lambda x: os.path.split(os.path.split(x)[0])[1]
    categories = map(get_category, images)
    category_map = sorted(set(categories))
    categories = np.array(map(category_map.index, categories))
    return categories, category_map


def load_and_extract(images):
    # placeholder variable for feature array
    features = None

    # go through each image and calculate features, saving them in the
    # feature array
    for i, image_path in enumerate(images):
        # display progress
        msg = "[%d / %d] %s" % (i, len(images), image_path)
        sys.stdout.write(msg + "\r")
        sys.stdout.flush()

        # load and extract features
        img = load_image(image_path)
        img_features = extract_features(img)
        if i == 0:
            features = np.empty((len(images), img_features.size), dtype='f4')
            sys.stdout.write(" "*len(msg) + "\r")
            print "Feature array has shape %s" % str(features.shape)
        features[i] = img_features

        # clear the output (the \r moves the cursor back to the
        # beginning of the line, so we can overwrite it)
        sys.stdout.write(" "*len(msg) + "\r")

    return features


if __name__ == "__main__":
    # get the list of images
    images = glob("./50_categories/*/*.jpg")

    # compute feature matrix
    features = load_and_extract(images)

    # create an integer mapping to categories
    categories, category_map = get_image_categories(images)

    # concatenate the features (X) and categories (Y)
    dataset = np.hstack([features, categories[:, None]])

    # save to disk
    filename = "./image_dataset.npy"
    np.save(filename, dataset)
    print "Saved features to '%s'" % filename

    filename = "./image_categories.npy"
    np.save(filename, category_map)
    print "Saved categories to '%s'" % filename
