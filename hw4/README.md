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

### Data

* `image_categories.npy` -- NumPy array of possible categories
* `image_classifier.pkl` -- pickled sklearn.ensemble.RandomForestClassifier

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
	* HOG (histogram of oriented gradients)

### Training the classifier

The actual training (and analysis) of the classifier takes place in
`hw4.ipynb`. It loads the saved features, trains a Random Forest
classifier on it, and displays a confusion matrix. Additionally, it
performs some cross-validation to provide an accuracy estimate.

The RF classifier has about 21.5% accuracy, which although not very
good, is significantly better than the 2.3% accuracy obtained by
random guessing (or even 3.4% accuracy obtained by guessing randomly
in proportion to category sizes). Looking at the confusion matrix
produced when there is no cross-validation, it is fairly clear that
the classifier is overfitting. This is probably a result of having too
many features (from the HOG); probably better performance would be
achieved with a larger dataset.

The three best features are have indices 817, 242, and 800 (in that
order). It is difficult to interpret the meaning of these features,
however, as they are part of the HOG (histogram of oriented
gradients).

## Verification

To run the classifier on a directory of verification images, you can
run from the command line:

`./verify.sh directory_name`

Or, alternately from within Python:

```
from image_classification import run_final_classifier
run_final_classifier("directory_name")
```

This will load the images in that directory, compute their features,
and attempt to classify them. The results will be printed to standard
out as well as being saved to a text file called `results.txt`.
