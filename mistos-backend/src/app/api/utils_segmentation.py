# import skimage
# import numpy as np
# import cv2
# import scipy
# from skimage import filters
# from skimage import segmentation
# from skimage.morphology import remove_small_objects

# csum = lambda z: np.cumsum(z)[:-1]
# dsum = lambda z: np.cumsum(z[::-1])[-2::-1]
# argmax = lambda x, f: np.mean(x[:-1][f == np.max(f)])  # Use the mean for ties.
# clip = lambda z: np.maximum(1e-30, z)

# def preliminaries(n, x):
#     """Some math that is shared across multiple algorithms."""
#     assert np.all(n >= 0)
#     x = np.arange(len(n), dtype=n.dtype) if x is None else x
#     assert np.all(x[1:] >= x[:-1])
#     w0 = clip(csum(n))
#     w1 = clip(dsum(n))
#     p0 = w0 / (w0 + w1)
#     p1 = w1 / (w0 + w1)
#     mu0 = csum(n * x) / w0
#     mu1 = dsum(n * x) / w1
#     d0 = csum(n * x**2) - w0 * mu0**2
#     d1 = dsum(n * x**2) - w1 * mu1**2
#     return x, w0, w1, p0, p1, mu0, mu1, d0, d1

# def GHT(n, x=None, nu=0, tau=0, kappa=0, omega=0.5, prelim=None):
#     assert nu >= 0
#     assert tau >= 0
#     assert kappa >= 0
#     assert omega >= 0 and omega <= 1
#     x, w0, w1, p0, p1, _, _, d0, d1 = prelim or preliminaries(n, x)
#     v0 = clip((p0 * nu * tau**2 + d0) / (p0 * nu + w0))
#     v1 = clip((p1 * nu * tau**2 + d1) / (p1 * nu + w1))
#     f0 = -d0 / v0 - w0 * np.log(v0) + 2 * (w0 + kappa *      omega)  * np.log(w0)
#     f1 = -d1 / v1 - w1 * np.log(v1) + 2 * (w1 + kappa * (1 - omega)) * np.log(w1)
#     return argmax(x, f0 + f1), f0 + f1

# def im2hist(im, zero_extents=False):
#     # Convert an image to grayscale, bin it, and optionally zero out the first and last bins.
#     max_val = np.iinfo(im.dtype).max
#     x = np.arange(max_val+1)
#     e = np.arange(-0.5, max_val+1.5)
#     assert len(im.shape) in [2, 3]
#     im_bw = np.amax(im[...,:3], -1) if len(im.shape) == 3 else im
#     n = np.histogram(im_bw, e)[0]
#     if zero_extents:
#         n[0] = 0
#         n[-1] = 0
#     return n, x, im_bw

# def segment_grayscale_2d_image(array, 
#                                radius_smooth = 5, 
#                                thresh_min = 0.05, thresh_max = 1, 
#                                radius_close = 6,
#                                min_object_size = 100
#                               ):
#     '''
#     This function excpects a single plane greyscale image and returns a labeled mask after image segmentation.
#     "radius_smooth": int, smoothes values after laplacian edge detection
#     "thresh_min / thresh_max": values to be accepted as edge after laplacian edge detection
    
#     '''
#     #Laplacian edge detection
#     laplacian = cv2.Laplacian(array,cv2.CV_64F)
#     laplacian = np.abs(laplacian)
    
#     # Map to values between -1 and 1
#     laplacian = laplacian/laplacian.max()
    
#     # smooth with mean filter
#     laplacian_smooth = filters.rank.mean(skimage.util.img_as_ubyte(laplacian), skimage.morphology.disk(radius_smooth))
    
#     # binarize
#     laplacian_bin = np.zeros_like(laplacian_smooth)
#     laplacian_bin[(laplacian_smooth >= thresh_min) & (laplacian_smooth <= thresh_max)] = 1
#     processed_img = laplacian_bin

# #     closing_selem = np.zeros((closing_selem_size,closing_selem_size), np.int)+1
#     closing_selem = skimage.morphology.disk(radius_close)
    
#     # fill holes
#     processed_img = skimage.morphology.binary_closing(processed_img, closing_selem)

#     # label all individual objects
#     distance = scipy.ndimage.distance_transform_edt(processed_img)
#     local_max_coords = skimage.feature.peak_local_max(distance, min_distance=7)
#     local_max_mask = np.zeros(distance.shape, dtype=bool)
#     local_max_mask[tuple(local_max_coords.T)] = True
#     markers = skimage.measure.label(local_max_mask)
#     processed_img = skimage.measure.label(processed_img)
    
#     # watershed
#     processed_img = segmentation.watershed(-distance, markers, mask=processed_img, watershed_line = True)
    
#     # remove small objects
#     processed_img = remove_small_objects(processed_img, min_object_size)
    
#     '''
#     TO DO: Remove large objects
#     '''
    
#     return processed_img, laplacian