import cv2
import numpy as np
from collections import deque
import math

pts = deque(maxlen=5)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
points = []
angles = []
lines = []

while(1):
	# Take each frame
	ret, frame = cap.read()
	frame = cv2.flip(frame, 1)

	# Convert BGR to HSV
	hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# define range of blue color in HSV
	lower_blue = np.array([105, 50, 50], dtype=np.uint8)
	upper_blue = np.array([120,255,255], dtype=np.uint8)

	# Threshold the HSV image to get only blue colors
	mask = cv2.inRange(hsvFrame, lower_blue, upper_blue)
	
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
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
 
	# update the points queue
	pts.appendleft(center)
 
	# loop over the set of tracked points
	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
 
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		#thickness = int(np.sqrt(100 / float(i + 1)) * 2.5)
		thickness=5
		cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), thickness)
	
	if pts[0] != None and pts[-1] != None:
		if math.sqrt((pts[0][0]-pts[-1][0])**2 + (pts[0][1]-pts[-1][1])**2) > 300:
			angle = math.atan2(pts[0][1] - pts[-1][1], pts[0][0] - pts[-1][0]) / math.pi * 180
			angles.append(angle)
			points.append( (pts[0][0] + (pts[-1][0] - pts[0][0]) // 2, pts[0][1] + (pts[-1][1] - pts[0][1]) // 2) )
			lines.append((pts[0], pts[-1]))
			for i in range(len(pts)):
				pts.pop()

	for p in lines:
		cv2.line(frame, p[0], p[1], (0, 0, 255), 3)
		
	# Bitwise-AND mask and original image

	cv2.imshow('frame',frame)
	cv2.imshow('mask',mask)
	
	k = cv2.waitKey(5) & 0xFF
	if k == 27:
		break

cv2.destroyAllWindows()