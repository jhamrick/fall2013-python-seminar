import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import pickle
from glob import glob
import sys
import os
from itertools import izip

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


def display_confusion_matrix(Y_test, Y_pred, categories):
    # compute confusion matrix
    confmat = confusion_matrix(Y_test, Y_pred)
    confmat_norm = confmat / confmat.sum(axis=1)[:, None].astype('f8')

    # plot the confusion matrix to visualize the accuracy
    fig, ax = plt.subplots()
    ax.matshow(confmat_norm, cmap='gray')

    ax.set_xticks(xrange(len(categories)))
    ax.set_xticklabels(categories, rotation=90, fontsize=7)
    ax.set_xlabel("Predicted Category")
    ax.set_yticks(xrange(len(categories)))
    ax.set_yticklabels(categories, rotation=0, fontsize=7)
    ax.set_ylabel("True Category")

    fig.set_figwidth(6)
    fig.set_figheight(6)


def run_final_classifier(directory):

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
    run_final_classifier(sys.argv[1])
