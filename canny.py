import numpy as np
import cv2
from matplotlib import pyplot as plt
from convolution_cpp_lib import matrix_convolution

# import the necessary packages
#from picamera.array import PiRGBArray
#from picamera import PiCamera
#import time

def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


def image_correlation(img, kernel):
    print("Usao u imageCorrelation")
    ret = matrix_convolution(img, kernel)
    print("ret size: ", ret.shape)

#    kernel_size = kernel.shape[0]
#    from_mid_len = kernel_size // 2
#    ret = np.zeros((img.shape[0] - from_mid_len, img.shape[1] - from_mid_len))
#    for i in range(img.shape[0] - kernel_size + 1):
#        for j in range(img.shape[1] - kernel_size + 1):

#            sum = 0
#            for x in range(kernel_size):
#                for y in range(kernel_size):
#                    sum += img[x + i, y + j] * kernel[x, y]
#            ret[i, j] = sum
    print("Izasao iz imageCorrelation")
    return ret


def gaussian_kernel(kernel_size=5, sigma=1.4):
    print("Usao u gaussianKernel")
    kernel = np.zeros((kernel_size, kernel_size))
    for i in range(-kernel_size // 2 + 1, kernel_size // 2 + 1):
        for j in range(-kernel_size // 2 + 1, kernel_size // 2 + 1):
            kernel[i + 2, j + 2] = np.exp(-(i ** 2 + j ** 2) / (2. * sigma ** 2))
    print("Izasao iz gaussianKernel")
    return kernel / np.sum(kernel)


def calc_gradients(img, kernel_type=0, eq_type=0):
    print("Usao u calcGradients")
    if kernel_type == 0:  # Sobel
        kernel_x = np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ])
    elif kernel_type == 1:  # Prewitt compass
        kernel_x = np.array([
            [-1, 0, 1],
            [-1, 0, 1],
            [-1, 0, 1]
        ])
    else:  # Scharr
        kernel_x = np.array([
            [-3, 0, 3],
            [-10, 0, 10],
            [-3, 0, 3]
        ])
    kernel_y = kernel_x.T

    img_x = image_correlation(img, kernel_x.astype(float))
    img_y = image_correlation(img, kernel_y.astype(float))

    magnitude = np.zeros(img_x.shape)
    orientation = np.zeros(img_x.shape, dtype=np.uint8)
    for i in range(img_x.shape[0]):
        for j in range(img_x.shape[1]):
            if eq_type == 0:
                magnitude[i, j] = np.sqrt(img_x[i, j] ** 2 + img_y[i, j] ** 2)
            else:
                magnitude[i, j] = np.abs(img_x[i, j]) + np.abs(img_y[i, j])

            angle = np.arctan2(img_y[i, j], img_x[i, j]) * 180 / np.pi
            # ALTERNATIVA:
            # if img_x[i, j] != 0:
            #     angle = img_y[i, j] / img_x[i, j]
            # else:
            #     angle = np.pi / 2
            # angle = np.arctan(angle) * 180 / np.pi
            while (angle < 0):
                angle += 180
            if angle > 112.5 and angle < 157.5:
                orientation[i, j] = 135
            elif angle > 67.5 and angle < 112.5:
                orientation[i, j] = 90
            elif angle > 22.5 and angle < 67.5:
                orientation[i, j] = 45
            else:
                orientation[i, j] = 0
    print("Izasao iz calcGradients")
    return magnitude, orientation


def nonmaximum_suppression(magnitude, orientation, upper_threshold):
    print("Usao u nonmaximumSuppression")
    returnImg = np.zeros((magnitude.shape[0], magnitude.shape[1]))
    for i in range(1, magnitude.shape[0] - 1):
        for j in range(1, magnitude.shape[1] - 1):
            # if magnitude[i, j] > upper_threshold:
            if orientation[i, j] == 135:
                if magnitude[i + 1, j + 1] < magnitude[i, j] and magnitude[i - 1, j - 1] < magnitude[i, j]:
                    returnImg[i, j] = magnitude[i, j]
            elif orientation[i, j] == 90:
                if magnitude[i, j + 1] < magnitude[i, j] and magnitude[i, j - 1] < magnitude[i, j]:
                    returnImg[i, j] = magnitude[i, j]
            elif orientation[i, j] == 45:
                if magnitude[i + 1, j - 1] < magnitude[i, j] and magnitude[i - 1, j + 1] < magnitude[i, j]:
                    returnImg[i, j] = magnitude[i, j]
            else:  # orientation[i,j] == 0:
                if magnitude[i - 1, j] < magnitude[i, j] and magnitude[i + 1, j] < magnitude[i, j]:
                    returnImg[i, j] = magnitude[i, j]
    print("Izasao iz nonmaximumSuppression")
    return returnImg


def double_threshold(edges_max, lower_threshold, upper_threshold):
    returnImg = np.zeros((edges_max.shape[0], edges_max.shape[1]))
    for i in range(1, edges_max.shape[0] - 1):
        for j in range(1, edges_max.shape[1] - 1):
            if edges_max[i, j] > upper_threshold:
                returnImg[i, j] = UPPER_THRESHOLD
            elif edges_max[i, j] > lower_threshold:
                returnImg[i, j] = LOWER_THRESHOLD
    return returnImg


def hysteresis_threshold(thresholded, magnitude, orientation, lower_threshold):
    print("Usao u hysteresisThreshold")
    changed_image = True
    it = 0
    while changed_image:
        changed_image = False
        it += 1
        print(it)
        for i in range(thresholded.shape[0]):
            for j in range(thresholded.shape[1]):

                if thresholded[i, j] != 255:
                    continue
                if orientation[i, j] == 135:
                    if i > 0 and j > 0:
                        if magnitude[i - 1, j - 1] >= lower_threshold and \
                                thresholded[i - 1, j - 1] != 64 and \
                                112.5 < orientation[i - 1, j - 1] < 157.5 and \
                                magnitude[i - 1, j - 1] > magnitude[i - 2, j] and \
                                magnitude[i - 1, j - 1] > magnitude[i, j - 2]:
                            thresholded[i - 1, j - 1] = 255
                            thresholded[i, j] = 64
                            changed_image = True
                    if i < thresholded.shape[0] - 1 and j < thresholded.shape[1] - 1:
                        if magnitude[i + 1, j + 1] >= lower_threshold and \
                                thresholded[i + 1, j + 1] != 64 and \
                                112.5 < orientation[i + 1, j + 1] < 157.5 and \
                                magnitude[i + 1, j + 1] > magnitude[i + 2, j] and \
                                magnitude[i + 1, j + 1] > magnitude[i, j + 2]:
                            thresholded[i + 1, j + 1] = 255
                            thresholded[i, j] = 64
                            changed_image = True

                elif orientation[i, j] == 90:
                    if i > 0:
                        if magnitude[i - 1, j] >= lower_threshold and \
                                thresholded[i - 1, j] != 64 and \
                                112.5 < orientation[i - 1, j] < 157.5 and \
                                magnitude[i - 1, j] > magnitude[i - 1, j - 1] and \
                                magnitude[i - 1, j] > magnitude[i - 1, j + 1]:
                            thresholded[i - 1, j] = 255
                            thresholded[i, j] = 64
                            changed_image = True
                    if i < thresholded.shape[1] - 1:
                        if magnitude[i + 1, j] >= lower_threshold and \
                                thresholded[i + 1, j] != 64 and \
                                112.5 < orientation[i + 1, j] < 157.5 and \
                                magnitude[i + 1, j] > magnitude[i + 1, j - 1] and \
                                magnitude[i + 1, j] > magnitude[i + 1, j + 1]:
                            thresholded[i + 1, j] = 255
                            thresholded[i, j] = 64
                            changed_image = True

                elif orientation[i, j] == 45:
                    if i < thresholded.shape[0] - 1 and j > 0:
                        if magnitude[i + 1, j - 1] >= lower_threshold and \
                                thresholded[i + 1, j - 1] != 64 and \
                                112.5 < orientation[i + 1, j - 1] < 157.5 and \
                                magnitude[i + 1, j - 1] > magnitude[i, j - 2] and \
                                magnitude[i + 1, j - 1] > magnitude[i + 2, j]:
                            thresholded[i + 1, j - 1] = 255
                            thresholded[i, j] = 64
                            changed_image = True
                    if i > 0 and j < thresholded.shape[1] - 1:
                        if magnitude[i - 1, j + 1] >= lower_threshold and \
                                thresholded[i - 1, j + 1] != 64 and \
                                112.5 < orientation[i - 1, j + 1] < 157.5 and \
                                magnitude[i - 1, j + 1] > magnitude[i - 2, j] and \
                                magnitude[i - 1, j + 1] > magnitude[i, j + 2]:
                            thresholded[i - 1, j + 1] = 255
                            thresholded[i, j] = 64
                            changed_image = True

                else:  # orientation[i, j] == 0:
                    if j > 0:
                        if magnitude[i, j - 1] >= lower_threshold and \
                                thresholded[i, j - 1] != 64 and \
                                112.5 < orientation[i, j - 1] < 157.5 and \
                                magnitude[i, j - 1] > magnitude[i - 1, j - 1] and \
                                magnitude[i, j - 1] > magnitude[i + 2, j - 1]:
                            thresholded[i, j - 1] = 255
                            thresholded[i, j] = 64
                            changed_image = True
                    if j < thresholded.shape[1] - 1:
                        if magnitude[i, j + 1] >= lower_threshold and \
                                thresholded[i, j + 1] != 64 and \
                                112.5 < orientation[i, j + 1] < 157.5 and \
                                magnitude[i, j + 1] > magnitude[i - 1, j + 1] and \
                                magnitude[i, j + 1] > magnitude[i + 1, j + 2]:
                            thresholded[i, j + 1] = 255
                            thresholded[i, j] = 64
                            changed_image = True

    for i in range(thresholded.shape[0]):
        for j in range(thresholded.shape[1]):
            if thresholded[i, j] == 64:
                thresholded[i, j] = 255

    print("Izasao iz hysteresisThreshold")
    return thresholded


def canny_edge_detector(img_orig, lower_threshold, upper_threshold, kernel_size=5):
    print("Usao u cannyEdgeDetector")
    img = image_correlation(img_orig, gaussian_kernel())
    magnitude, orientation = calc_gradients(img)
    edges_max = nonmaximum_suppression(magnitude, orientation, upper_threshold)
    thresholded = double_threshold(edges_max, lower_threshold, upper_threshold)
    cv2.imshow("thresholded", thresholded)
    edges = hysteresis_threshold(thresholded, magnitude, orientation, lower_threshold)
    print("Izasao iz cannyEdgeDetector")
    cv2.imwrite("edges_original.jpg", edges[0:img_orig.shape[0], 0:img_orig.shape[1]])
    return edges[0:img_orig.shape[0], 0:img_orig.shape[1]]


global LOWER_THRESHOLD
global UPPER_THRESHOLD
LOWER_THRESHOLD = 127
UPPER_THRESHOLD = 255

#camera = PiCamera()
#rawCapture = PiRGBArray(camera)
# allow the camera to warmup
#time.sleep(0.1)
# grab an image from the camera
#camera.capture(rawCapture, format="bgr")
#img = rawCapture.array

img = cv2.imread(r"/home/bici/Desktop/rpi-project/images/lena.jpg")
gray = rgb2gray(img)

canny_edge_detector(gray, 30,50)
