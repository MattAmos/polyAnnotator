#! /usr/bin/env python2

import json
import os
import skvideo.io
from skimage import io

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
		print(self.videoFile)
		cap = skvideo.io.vreader(self.videoFile)
		metadata = skvideo.io.ffprobe(self.videoFile)

		# Consume first frame to determine video settings
		frame = next(cap, None)
		if frame is None:
			print('[ERR] Failed to open video file "{}"'.format(self.videoFile))
			exit()

		numFrames = metadata['video']['@nb_frames']
		videoDict = {'path' : self.videoFile, 'width' : frame.shape[1], 'height' : frame.shape[0], 'frame' : []}

		self.frameNo = 0
		for frame in cap:
			frameDict = {'frameNo' : self.frameNo, 'annotation' : []}
			videoDict['frame'].append(frameDict)
			print('[{0:5d}/{1:5d}] {2}/{3:010d}.{4}'.format(self.frameNo, int(numFrames), self.trueName, self.frameNo, 'JPG'))
			io.imsave('{0}/{1:010d}.{2}'.format(self.trueName, self.frameNo, 'JPG'), frame)
			self.frameNo += 1
		if not os.path.isfile('{0}.{1}'.format(self.trueName, 'json')):
			with open('{0}.{1}'.format(self.trueName, 'json'), 'w') as f:
				json.dump(videoDict, f)
			print('[LOG] Created annotation file {0}'.format('{0}.{1}'.format(self.trueName, 'json')))
		print('[LOG] Saved {0} images to directory {1}'.format(numFrames, self.trueName))
		cap.release()
	