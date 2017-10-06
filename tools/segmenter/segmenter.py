#! python3
#! PY_PYTHON=3

import json
import os.path
from PIL import Image, ImageDraw

COLOUR = 127
BORDER = 8

class Segmenter:
	def __init__(self, argv):
		self.polyPool = []
		self.currDir = ""
		if len(argv) >= 2:
			self.currDir = argv[1]
			self.readInPolygons()
			self.drawImages()
		else:
			print("[ERR] Usage: python main.py <path>")

	def readInPolygons(self):
		if(os.path.isfile(self.currDir + ".json")):
			with open(self.currDir + ".json", 'r') as f:
				temp = json.load(f)
				if len(temp) > 0:
					self.polyPool = list(temp)
					print("[LOG] Read polygons data of {} frames from {}".format(len(self.polyPool), self.currDir + ".json"))

	def drawImages(self):
		numPoly = 0; numPts = 0
		for p in self.polyPool:
			raw = Image.open(self.currDir + "/" + p[0])
			seg = Image.new('P', raw.size, 0)
			d = ImageDraw.Draw(seg)
			firstPt = None
			numPoly += len(p[1])
			for poly in p[1]:
				if len(poly) > 0:
					firstPt = poly[0]
				dPolygon = [];	dLine = []
				for pt in poly:
					dPolygon += pt
					numPts += 1
				dPolygon += firstPt
				d.polygon(dPolygon, COLOUR, 255)
				d.line(dPolygon, 255, BORDER)
			seg.save(self.currDir + "_seg/" + p[0], raw.format)
		print("[LOG] {} images processed, {} points drawn constituting {} polygons".format(len(self.polyPool), numPts, numPoly))
