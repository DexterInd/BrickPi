#!/usr/bin/env python
import numpy as np
import cv2
from matplotlib import pyplot as plt

img = cv2.imread('gridlines3.jpg',0)

# Initiate FAST object with default values
fast = cv2.FastFeatureDetector(20)

# find and draw the keypoints with FAST algorithm
kp = fast.detect(img,None)
img2 = cv2.drawKeypoints(img, kp, color=(255,0,0))

# Print all default params
print "Threshold: ", fast.getInt('threshold')
print "nonmaxSuppression: ", fast.getBool('nonmaxSuppression')
print "Total Keypoints with nonmaxSuppression: ", len(kp)

cv2.imwrite('true.png',img2)

plt.imshow(img2),plt.show()

