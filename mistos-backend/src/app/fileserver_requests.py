import pickle
import os
import shutil

def delete_file(path):
    os.remove(path)

def delete_folder(path):
    shutil.rmtree(path)

def save_measurement(measurement, path):
    with open(path, "wb") as _file:
        pickle.dump(measurement, _file)

def load_measurement(path):
    with open(path, "rb") as _file:
        measurement = pickle.load(_file)
    return measurement

def save_classifier(clf, path):
    with open(path, "wb") as _file:
        pickle.dump(clf, _file)

def load_classifier(path):
    with open(path, "rb") as _file:
        clf = pickle.load(_file)
    return clf

def save_classifier_test_train(test_train, path):
    with open(path, "wb") as _file:
        pickle.dump(test_train, _file)

def load_classifier_test_train(path):
    with open(path, "rb") as _file:
        test_train = pickle.load(_file)
    return test_train