"""Image classification and verification module

To run the classifier on a directory of verification images, you can
run from the command line:

`./verify.sh directory_name pickled_classifier`

Or, alternately from within Python:

```
from image_classification import run_final_classifier
run_final_classifier("directory_name", "pickled_classifier")
```

This will load the images in that directory, compute their features,
and attempt to classify them. The results will be printed to standard
out as well as being saved to a text file called `results.txt`.

"""

# built-in
import os
import pickle
import sys
import warnings
from glob import glob
from itertools import izip
# external
import matplotlib.pyplot as plt
import numpy as np
import scipy
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.cross_validation import KFold
# local
from image_processing import load_and_extract

# turn off warnings
warnings.filterwarnings('ignore')


def train_classifier(X, Y, save=False, rso=None):
    """Train a random forest classifier on the data.

    Parameters
    ----------
    X : (N, M) numpy.ndarray
        Feature array, where N is the number of data points and M is
        the number of features.
    Y : (N,) numpy.ndarray
        Observation vectory, where N is the number of observations.
    save : bool (optional)
        Whether to save (pickle) the classifier to disk
    rso : numpy.random.RandomState (optional)
        Random state object

    Returns
    -------
    clf : sklear.ensemble.RandomForestClassifier

    """
    clf = RandomForestClassifier(
        n_estimators=50,
        n_jobs=-1,
        compute_importances=True,
        random_state=rso)
    clf.fit(X, Y)

    # optionally save the pickled classifier to disk
    if save:
        with open("trained_classifier.p", "w") as fh:
            pickle.dump(clf, fh)

    return clf


def cross_validate(X, Y, predict_func, nidx=10, rso=None):
    """Cross validate a classifier using k-fold cross validation, and
    print out the accuracy for each fold and then the mean and
    standard error across folds.

    Parameters
    ----------
    X : (N, M) numpy.ndarray
        Feature array, where N is the number of data points and M is
        the number of features.
    Y : (N,) numpy.ndarray
        Observation vectory, where N is the number of observations.
    predict_func : function
        The prediction function, which should have the following call
        signature:
            predict_funct(X_train, Y_train, X_test, rso=None)
    nidx : int (optional)
        The number of folds to use
    rso : numpy.random.RandomState (optional)
        Random state object

    """
    indices = KFold(Y.size, n_folds=nidx, random_state=rso)
    stats = []
    for i, (train_idx, test_idx) in enumerate(indices):
        Y_pred = predict_func(X[train_idx], Y[train_idx], X[test_idx], rso=rso)
        accuracy = accuracy_score(Y[test_idx], Y_pred)
        print "[%d / %d] Fraction correctly classified: %.3f" % (
            i+1, nidx, accuracy)
        sys.stdout.flush()
        stats.append(accuracy)
    mean = np.mean(stats)
    sem = scipy.stats.sem(stats)
    print "Accuracy: %.3f +/- %.3f" % (mean, sem)


def display_confusion_matrix(Y_test, Y_pred, normalize=True):
    """Compute and display a confusion matrix for prediction accuracy.

    Parameters
    ----------
    Y_test : np.ndarray
        True (integer) category values
    Y_pred : np.ndarray
        Predicted (integer) category values
    normalize : bool (optional)
        Whether to normalize the confusion matrix to indicate
        proportions

    """

    categories = np.load("image_categories.npy")
    # compute confusion matrix
    confmat = confusion_matrix(Y_test, Y_pred)
    if normalize:
        confmat = confmat / confmat.sum(axis=1)[:, None].astype('f8')

    # plot the confusion matrix to visualize the accuracy
    fig, ax = plt.subplots()
    ax.matshow(confmat, cmap='gray')

    ax.set_xticks(xrange(len(categories)))
    ax.set_xticklabels(categories, rotation=90, fontsize=7)
    ax.set_xlabel("Predicted Category")
    ax.set_yticks(xrange(len(categories)))
    ax.set_yticklabels(categories, rotation=0, fontsize=7)
    ax.set_ylabel("True Category")

    fig.set_figwidth(6)
    fig.set_figheight(6)


def run_final_classifier(path, forest):
    """Run a random forest classifier on a directory of verification
    images. This function saves a file to disk called 'results.txt',
    which is formatted like so:

    filename        predicted_class
    ------------------------------
    bat_0001.jpg    cormorant
    bat_0002.jpg    conch
    bat_0003.jpg    raccoon
    bat_0004.jpg    blimp
    bat_0005.jpg    blimp
    ...

    This function expects the list of categories to already exist in a
    file 'image_categories.npy'.

    Parameters
    ----------
    path : str
        Name of the directory containing verification images
    forest : str
        Name of the pickled random forest classifier file

    """

    # get the list of images
    images = glob("%s/*.jpg" % path)
    # get the list of categories
    categories = np.load("./image_categories.npy")

    # compute feature matrix
    features = load_and_extract(images)

    # load the classifier
    with open(forest, "r") as fh:
        clf = pickle.load(fh)

    # make predictions
    Y_pred = clf.predict(features)

    # save the results to file
    results_file = "./results.txt"
    with open(results_file, "w") as fh:
        def write(msg):
            sys.stdout.write(msg)
            fh.write(msg)

        write("filename\tpredicted_class\n")
        write("-"*30 + "\n")

        for image, pred in izip(images, Y_pred):
            filename = os.path.split(image)[1]
            line = "%s\t%s\n" % (filename, categories[pred])
            write(line)

    print "Results saved to '%s'." % results_file


if __name__ == "__main__":
    # run a given classifier on images in a given directory
    if len(sys.argv) < 3:
        print "Invalid number of arguments (expected 'path' and 'forest')."
        sys.exit(1)
    run_final_classifier(sys.argv[1], sys.argv[2])
