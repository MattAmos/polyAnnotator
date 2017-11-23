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
					self.polyPool = temp
					print("[LOG] Read polygons data of {} frames from {}".format(len(self.polyPool["frame"]), self.currDir + ".json"))

	def drawImages(self):
		numPoly = 0; numPts = 0
		for f in self.polyPool["frame"]:
			numPoly += len(self.polyPool["frame"][f]["annotation"])
			frame = self.polyPool["frame"][f]
			raw = Image.open(self.currDir + "/" + '{0:015d}.{1}'.format(frame["frameno"], '.JPG'))
			seg = Image.new('P', raw.size, 0)
			d = ImageDraw.Draw(seg)
			for p in self.polyPool["frame"][f]["annotation"]:
				numPts += len(p["point"])
				firstPt = None
				# Account for linking back up to first point at end of poly
				if len(p["point"]) > 0:
					firstPt = p[0]
				dPolygon = [];	dLine = []
				for pt in p:
					dPolygon += [pt["x"], pt["y"]]
					numPts += 1
				# Add on first poly
				dPolygon += [firstPt["x"], firstPt["y"]]
				d.polygon(dPolygon, COLOUR, 255)
				d.line(dPolygon, 255, BORDER)
			seg.save(self.currDir + "_seg/" + p[0], raw.format)
		print("[LOG] {} images processed, {} points drawn constituting {} polygons".format(len(self.polyPool["frame"]), numPts, numPoly))
