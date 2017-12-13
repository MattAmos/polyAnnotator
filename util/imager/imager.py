#! /usr/bin/env python2

from __future__ import print_function
from copy import deepcopy

import json
import os
import cv2

class Imager:
	def __init__(self, argv):
		self.frameNo = 0	# Frame number dictating current video position
		self.videoFile = "" # Video file path
		self.trueName = ""
		if len(argv) >= 2:
			self.videoFile = argv[1]
			if os.path.isfile(self.videoFile):
				dotIndex = self.videoFile.rfind('.')
				if dotIndex != -1:
					self.trueName = self.videoFile[:dotIndex]
				if(os.path.isdir(self.trueName) == False):
					print('[ERR] Directory "{0}" has not been created'.format(self.trueName))
					exit()
				self.processVideo()
			else:
				print('[ERR] Could not find file "{0}"'.format(self.videoFile))
		else:
			print('[ERR] Usage: python main.py <path>')

	def processVideo(self):
		cap = cv2.VideoCapture(self.videoFile)
		if cap.isOpened() == False:
			print('[ERR] Failed to open video file "{}"'.format(self.videoFile))
			exit()
		ret, frame = cap.read()
		videoDict = {'path' : self.videoFile, 'width' : frame.shape[1], 'height' : frame.shape[0], 'frame' : []}

		numFrames = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
		divider = int(numFrames/100.0)
		while(self.frameNo < numFrames):
			frameDict = {'frameNo' : self.frameNo, 'annotation' : []}
			videoDict['frame'].append(frameDict)
			print('[{0:5d}/{1:5d}] {2}/{3:010d}.{4}'.format(self.frameNo, numFrames, self.trueName, self.frameNo, 'JPG'))
			cv2.imwrite('{0}/{1:010d}.{2}'.format(self.trueName, self.frameNo, 'JPG'), frame)
			self.frameNo += 1
			ret, frame = cap.read()
		with open('{0}.{1}'.format(self.trueName, 'json'), 'w') as f:
			json.dump(videoDict, f)
		print('[LOG] Saved {0} images to directory {1}. Created annotation file {2}'.format(numFrames, self.trueName, '{0}.{1}'.format(self.trueName, 'json')))
		cap.release()
	