# Homework 4: Machine Learning

Author: Jessica Hamrick  
Email: `jhamrick@berkeley.edu`

## Files

### Code

* `image_processing.py` -- image processing and feature extraction module
* `image_classification.py` -- image classification and verification module
* `hw4.ipynb` -- IPython notebook for training the classifier and
  analyzing its performance
* `util.py` -- Miscellaneous helper functions
* `verify.sh` -- helper script to run `image_classification.py`

### Data

* `image_categories.npy` -- NumPy array of possible categories
* `image_dataset.npy` -- NumPy array of features for training data

## Training

### Computing features

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

The features that are computed are:
	* mean of each of the R/G/B channels
	* covariance between the R/G/B channels
	* summary statistics of image entropy (sum, mean, variance)

I also tried playing around with HOG (histogram of oriented gradients)
features, but this produced too many features and the classifier was
badly overfitting -- I think they are probably better for larger
datasets.

### Training the classifier

The actual training (and analysis) of the classifier takes place in
`hw4.ipynb`. It loads the saved features, trains a Random Forest
classifier on it, and displays a confusion matrix. Additionally, it
performs some cross-validation to provide an accuracy estimate.

Accuracies are as follows:

* RF classifier: 20.7%
* Random guessing: 2.1%
* Random guessing in proportion to category sizes: 3.7%

The best features are:

* variance of the image entropy
* the covariance between blue and green channels
* the covariance between red and blue channels

## Verification

First, you will need to train the classifier by running the code in
the IPython notebook (as in the section above); you only need ro run
the first four cells. This will save the classifier to a file called
`trained_classifier.p`.

Once you have done that, you can run the classifier on a directory of
verification images from the command line:

`./verify.sh directory_name pickled_classifier`

Or, alternately from within Python:

```
from image_classification import run_final_classifier
run_final_classifier("directory_name", "pickled_classifier")
```

This will load the images in that directory, compute their features,
and attempt to classify them. The results will be printed to standard
out as well as being saved to a text file called `results.txt`.
