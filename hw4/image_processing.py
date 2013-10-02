import numpy as np
import skimage.exposure
import skimage.feature
import skimage.filter
import skimage.io
from glob import glob
import os
import sys


def load_image(img_path, n=128):
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
        The dimension to scale the image to (it will be the same for
        both width and height)

    Returns
    -------
    img : numpy.ndarray with shape (n, n, 3)

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

    # add extra space to the other dimension so it is also size n
    if shape == (n, n):
        return img
    idx = np.argmin(shape)
    bufshape = list(img.shape)
    bufshape[idx] = n - min(shape)
    buffer = np.ones(bufshape)
    b0, b1 = np.array_split(buffer, 2, axis=idx)
    parts = [b0, img]
    if b1.size > 1:
        parts.append(b1)
    img = np.concatenate(parts, axis=idx)

    return img


def extract_features(img):
    """Extract a vector of features from an image. The feature vector is
    flat, but has the following components:

        1) Mean of R, G, and B channels
        2) Covariance between R, G, and B channels
        3) Histogram of oriented gradients

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
    # covariance between channels
    cov = np.cov(RGB).ravel()
    # histogram of oriented gradients
    hog = skimage.feature.hog(
        img.mean(axis=-1),
        orientations=4,
        pixels_per_cell=(8, 8),
        cells_per_block=(1, 1))

    # concatenate all the features together
    feature_vec = np.concatenate([mean, cov, hog])

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
