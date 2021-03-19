

from itertools import combinations_with_replacement
import itertools
import numpy as np
from skimage import filters, feature
from skimage import img_as_float32
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestClassifier
from app.api.utils_transformations import binary_mask_to_multilabel

try:
    from sklearn.exceptions import NotFittedError

    has_sklearn = True
except ImportError:
    has_sklearn = False

    class NotFittedError(Exception):
        pass


def semi_automatic_classification(img_array, label_array, remove_bg_label=True):
    '''
    Expects an image of shape (z,c,y,x) and labels of shape (z,y,x). Returns the prediction labels.
    Background should always be labeled with class 1:
        If remove_bg_label is true, all labels except 0 will be reduced by one. This will effectively remove label 1. 
    '''
    clf = RandomForestClassifier(
        n_estimators=50, n_jobs=-1, max_depth=8, max_samples=0.05
    )

    features = multiscale_basic_features(img_array, multichannel=True)
    classified_img, clf = fit_segmenter(label_array, features, clf)

    if remove_bg_label:
        classified_img[classified_img >
                       0] = classified_img[classified_img > 0] - 1

    if len(classified_img.shape) == 2:
        classified_img = classified_img[np.newaxis, ...]

    return binary_mask_to_multilabel(classified_img)[0], clf

# Taken and adapted (mostly directly copied) from
# https://github.com/plotly/dash-sample-apps/blob/master/apps/dash-image-segmentation/trainable_segmentation.py
# 23.01.2021, 11:10


def _texture_filter(gaussian_filtered):
    H_elems = [
        np.gradient(np.gradient(gaussian_filtered)[ax0], axis=ax1)
        for ax0, ax1 in combinations_with_replacement(range(gaussian_filtered.ndim), 2)
    ]
    eigvals = feature.hessian_matrix_eigvals(H_elems)
    return eigvals


def _mutiscale_basic_features_singlechannel(
    img, intensity=True, edges=True, texture=True, sigma_min=0.5, sigma_max=16
):
    """Features for a single channel nd image.

    Parameters
    ----------
    """
    # computations are faster as float32
    img = np.ascontiguousarray(img_as_float32(img))
    sigmas = np.logspace(
        np.log2(sigma_min),
        np.log2(sigma_max),
        num=int(np.log2(sigma_max) - np.log2(sigma_min) + 1),
        base=2,
        endpoint=True,
    )
    all_filtered = Parallel(n_jobs=-1, prefer="threads")(
        delayed(filters.gaussian)(img, sigma) for sigma in sigmas
    )
    features = []
    if intensity:
        features += all_filtered
    if edges:
        all_edges = Parallel(n_jobs=-1, prefer="threads")(
            delayed(filters.sobel)(filtered_img) for filtered_img in all_filtered
        )
        features += all_edges
    if texture:
        all_texture = Parallel(n_jobs=-1, prefer="threads")(
            delayed(_texture_filter)(filtered_img) for filtered_img in all_filtered
        )
        features += itertools.chain.from_iterable(all_texture)
    return features


def multiscale_basic_features(
    image,
    multichannel=True,
    intensity=True,
    edges=True,
    texture=True,
    sigma_min=0.5,
    sigma_max=16,
):
    """Local features for a single- or multi-channel nd image.

    Intensity, gradient intensity and local structure are computed at
    different scales thanks to Gaussian blurring.

    Parameters
    ----------
    image : ndarray
        Input image, which can be grayscale or multichannel.
    multichannel : bool, default False
        True if the last dimension corresponds to color channels.
    intensity : bool, default True
        If True, pixel intensities averaged over the different scales
        are added to the feature set.
    edges : bool, default True
        If True, intensities of local gradients averaged over the different
        scales are added to the feature set.
    texture : bool, default True
        If True, eigenvalues of the Hessian matrix after Gaussian blurring
        at different scales are added to the feature set.
    sigma_min : float, optional
        Smallest value of the Gaussian kernel used to average local
        neighbourhoods before extracting features.
    sigma_max : float, optional
        Largest value of the Gaussian kernel used to average local
        neighbourhoods before extracting features.

    Returns
    -------
    features : np.ndarray
        Array of shape ``(n_features,) + image.shape``
    """
    if image.ndim >= 3 and multichannel:
        all_results = (
            _mutiscale_basic_features_singlechannel(
                image[..., dim],
                intensity=intensity,
                edges=edges,
                texture=texture,
                sigma_min=sigma_min,
                sigma_max=sigma_max,
            )
            for dim in range(image.shape[-1])
        )
        features = list(itertools.chain.from_iterable(all_results))
    else:
        features = _mutiscale_basic_features_singlechannel(
            image,
            intensity=intensity,
            edges=edges,
            texture=texture,
            sigma_min=sigma_min,
            sigma_max=sigma_max,
        )
    return np.array(features, dtype=np.float32)


def fit_segmenter(labels, features, clf):
    """
    Segmentation using labeled parts of the image and a classifier.

    Parameters
    ----------
    labels : ndarray of ints
        Image of labels. Labels >= 1 correspond to the training set and
        label 0 to unlabeled pixels to be segmented.
    features : ndarray
        Array of features, with the first dimension corresponding to the number
        of features, and the other dimensions correspond to ``labels.shape``.
    clf : classifier object
        classifier object, exposing a ``fit`` and a ``predict`` method as in
        scikit-learn's API, for example an instance of
        ``RandomForestClassifier`` or ``LogisticRegression`` classifier.

    Returns
    -------
    output : ndarray
        Labeled array, built from the prediction of the classifier trained on
        ``labels``.
    clf : classifier object
        classifier trained on ``labels``

    Raises
    ------
    NotFittedError if ``self.clf`` has not been fitted yet (use ``self.fit``).
    """
    training_data = features[:, labels > 0].T
    training_labels = labels[labels > 0].ravel()
    clf.fit(training_data, training_labels)
    data = features[:, labels == 0].T
    predicted_labels = clf.predict(data)
    output = np.copy(labels)
    output[labels == 0] = predicted_labels
    return output, clf


def predict_proba_segmenter(features, clf, threshold=0.5):
    sh = features.shape
    features = features.reshape((sh[0], np.prod(sh[1:]))).T
    try:
        # Returns array of shape (n_pixels, 2). Last dimension is (P(false), P(True)). For Multiclass, a List of len n_classes is returned
        predicted_labels = clf.predict_proba(features)[:, 1]
        predicted_labels = np.where(predicted_labels > threshold, 1, 0)

    except NotFittedError:
        raise NotFittedError(
            "You must train the classifier `clf` first"
            "for example with the `fit_segmenter` function."
            "Also not suitable for multiclass yet"
        )
    output = predicted_labels.reshape(sh[1:])
    return output


def predict_segmenter(features, clf):
    """
    Segmentation of images using a pretrained classifier.

    Parameters
    ----------
    features : ndarray
        Array of features, with the first dimension corresponding to the number
        of features, and the other dimensions are compatible with the shape of
        the image to segment.
    clf : classifier object
        trained classifier object, exposing a ``predict`` method as in
        scikit-learn's API, for example an instance of
        ``RandomForestClassifier`` or ``LogisticRegression`` classifier. The
        classifier must be already trained, for example with
        :func:`fit_segmenter`.
    features_func : function, optional
        function computing features on all pixels of the image, to be passed
        to the classifier. The output should be of shape
        ``(m_features, *labels.shape)``. If None,
        :func:`multiscale_basic_features` is used.

    Returns
    -------
    output : ndarray
        Labeled array, built from the prediction of the classifier.
    """
    sh = features.shape
    features = features.reshape((sh[0], np.prod(sh[1:]))).T
    try:
        predicted_labels = clf.predict(features)
    except NotFittedError:
        raise NotFittedError(
            "You must train the classifier `clf` first"
            "for example with the `fit_segmenter` function."
        )
    output = predicted_labels.reshape(sh[1:])
    return output
