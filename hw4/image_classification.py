# built-in
import os
import pickle
import sys
from glob import glob
from itertools import izip
# external
import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
# local
from image_processing import load_and_extract


def split_data(dataset, ftrain=0.9, rso=None):
    data = dataset.copy()
    if rso is None:
        np.random.shuffle(data)
    else:
        rso.shuffle(data)

    # split the dataset into input/output and testing/training
    ntrain = int(len(dataset) * ftrain)

    X = preprocessing.scale(data[:, :-1])
    X_train = X[:ntrain]
    X_test = X[ntrain:]

    Y = data[:, -1]
    Y_train = Y[:ntrain]
    Y_test = Y[ntrain:]

    return X_train, X_test, Y_train, Y_test


def train_classifier(X, Y, save=False, rso=None):
    # train a random forest classifier on the data
    clf = RandomForestClassifier(random_state=rso)
    clf.fit(X, Y)

    # optionally save the pickled classifier to disk
    if save:
        with open("image_classifier.pkl", "w") as fh:
            pickle.dump(clf, fh)

    return clf


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


def run_final_classifier(directory):
    """Run the classifier on a directory of verification images. This
    function saves a file to disk called 'results.txt', which is
    formatted like so:

    filename        predicted_class
    ------------------------------
    bat_0001.jpg    cormorant
    bat_0002.jpg    conch
    bat_0003.jpg    raccoon
    bat_0004.jpg    blimp
    bat_0005.jpg    blimp
    ...

    This function expects the classifier and list of categories to
    already exist, in files named 'image_classifier.pkl' and
    'image_categories.npy', respectively.

    Parameters
    ----------
    directory : str
        Name of the directory containing verification images

    """

    # get the list of images
    images = glob("%s/*.jpg" % directory)
    # get the list of categories
    categories = np.load("./image_categories.npy")

    # compute feature matrix
    features = load_and_extract(images)

    # load the classifier
    with open("./image_classifier.pkl", "r") as fh:
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
    # run the final classifier on images in a directory which should
    # be passed as an argument
    if len(sys.argv) < 2:
        print "No verification directory specified (should be first argument)."
        sys.exit(1)
    run_final_classifier(sys.argv[1])
