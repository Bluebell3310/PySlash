import cv2
import numpy as np
from collections import deque
import math

BLUE_LOWER = 105
BLUE_UPPER = 120
GREEN_LOWER = 80
GREEN_UPPER = 100

class Detector:
	def __init__(self, camera, color):
		self.cap = cv2.VideoCapture(camera)
		self.color = color
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
		self.points = []
		self.angles = []
	
	def get_color_center(self):
		ret, frame = self.cap.read()
		frame = cv2.flip(frame, 1)

		# Convert BGR to HSV
		hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		
		if self.color == "blue":
			# define range of blue color in HSV
			lower_color = np.array([BLUE_LOWER, 50, 50], dtype=np.uint8)
			upper_color = np.array([BLUE_UPPER, 255, 255], dtype=np.uint8)
			# Threshold the HSV image to get only blue colors
			mask = cv2.inRange(hsvFrame, lower_color, upper_color)
		elif self.color == "green":
			# define range of green color in HSV
			lower_color = np.array([GREEN_LOWER, 50, 50], dtype=np.uint8)
			upper_color = np.array([GREEN_UPPER, 255, 255], dtype=np.uint8)
			# Threshold the HSV image to get only green colors
			mask = cv2.inRange(hsvFrame, lower_color, upper_color)
		
		# apply a series of erosions and dilations to the mask
		# using an elliptical kernel
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
		mask = cv2.erode(mask, kernel, iterations = 1)
		mask = cv2.dilate(mask, kernel, iterations = 1)
		
		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = None

		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = ( int(np.interp(M["m10"] / M["m00"], [0, 600], [0, 400])), \
					   int(np.interp(M["m01"] / M["m00"], [0, 600], [0, 400])) )
	 
			# only proceed if the radius meets a minimum size
			if radius > 10:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame, center, 5, (0, 0, 255), -1)
		
		return center