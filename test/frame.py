#! python3
#! PY_PYTHON=3

import sys, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

SIZE = 10
BRUSH_SIZE = 5
UNDO_SIZE = 10

##### GENERIC FRAME CLASS #####
class Frame(QFrame):
	def __init__(self, parent, image):
		super().__init__()
		self.parent = parent
		# Containers
		self.polyIndex = 0
		self.points = []
		self.polygons = []
		self.undoBuff = []
		self.currPoint = []
		self.image = image
		# Key variables
		self.saved = False
		self.shiftKey = False
		self.ctrlKey = False
		self.clicked = False
		# Movement point variables
		self.oldPt = []
		self.newPt = []
		self.initUI()

	def initUI(self):
		self.setFocusPolicy(Qt.StrongFocus)
		QToolTip.setFont(QFont('SansSerif', 10))
		self.setMouseTracking(True)

		self.center()
		self.setWindowTitle('Poly Annotator v0.02')
		pixmap = QPixmap("icon/web.png")
		self.setWindowIcon(QIcon(pixmap))
		self.setGeometry(0, 0, self.image.width(), self.image.height())
		self.show()

	def getQPoints(self, pointsList):
		qPoints = []
		for i in range(len(pointsList)):
			x = pointsList[i][0] + BRUSH_SIZE/2.0
			y = pointsList[i][1] - BRUSH_SIZE/2.0
			if x < 0 : x = 0
			if y < 0 : y = 0
			if x > self.image.width() : x = self.image.width()
			if y > self.image.height() : y = self.image.height()
			qPoints += [QPoint(x, y)]  
		return qPoints

	def selectPoly(self, offset):
		if len(self.polygons) == 0 and len(self.points) > 0:
			self.polygons.append(self.points)
		elif len(self.points) > 0:
			self.polygons[self.polyIndex] = list(self.points)

		if len(self.polygons) > 0:
			self.polyIndex = (self.polyIndex + offset) % len(self.polygons)
			self.points = self.polygons[self.polyIndex]
		else:
			self.polyIndex = 0
			self.points = []

	def addPoly(self):
		if len(self.points) > 0:
			self.polygons.insert(self.polyIndex, self.points)
			self.polyIndex += 1
			self.points = []

	def delPoly(self):
		self.polygons.remove(self.polygons[self.polyIndex])
		self.selectPoly(-1)

	def clearPoints(self):
		self.points = []
		if len(self.polygons) > 0:
			self.delPoly()

	### Drawing Functions ###
	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)
		self.draw(qp)
		qp.end()
		self.setWindowTitle('Poly Annotator v0.02')
		pixmap = QPixmap("icon/web.png")
		self.setWindowIcon(QIcon(pixmap))
		self.update()
		self.setMouseTracking(True)

	def draw(self, qp):
		# First, draw the image
		qp.drawImage(QPoint(0,0), self.image)
		# Then draw all other polygons
		brush = QBrush(Qt.SolidPattern)
		color = QColor()
		if len(self.polygons) > 0:
			count = 0
			for i in range(0, 360, int(360/len(self.polygons))):
				qPoints = self.getQPoints(self.polygons[count]) 
				h = i
				s = 90 + random.random()*10
				l = 50 + random.random()*10
				color.setHsl(h, s, l, 127)
				brush.setColor(color)
				qp.setBrush(brush)
				qp.drawPolygon(QPolygon(qPoints))
				count += 1
		# Then draw all points
		qp.setPen(QPen(Qt.white, BRUSH_SIZE, Qt.SolidLine))
		size = self.size()
		qPoints = self.getQPoints(self.points)
		for pt in self.points:
			qp.drawEllipse(pt[0], pt[1], BRUSH_SIZE, BRUSH_SIZE)
		qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
		qp.drawPolygon(QPolygon(qPoints))

		color.setHsl(255, 255, 255, 127)
		brush.setColor(color)
		qp.setBrush(brush)
		qp.drawPolygon(QPolygon(qPoints))

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def mouseMoveEvent(self, e):
		x = e.x()
		y = e.y()
		if self.clicked and self.oldPt != []:
			temp = next((pt for pt in self.points if pt == self.oldPt), [])
			if temp != []:
				index = self.points.index(self.oldPt)
				self.points.remove(temp)
				self.points.insert(index, [x, y])
				self.oldPt = [x, y]
			# self.newPt = [x, y]

	def mousePressEvent(self, e):
		if e.button() == Qt.LeftButton:
			x = e.x()
			y = e.y()
			self.clicked = True
			temp = next((pt for pt in self.points if (pt[0] - x)**2 + (pt[1] - y)**2 < (SIZE + SIZE)**2), [])
			if temp != []:
				self.undoBuff.append(list(self.points))
				# print(temp)
				self.oldPt = temp

	def mouseReleaseEvent(self, e):
		if e.button() == Qt.LeftButton:
			x = e.x()
			y = e.y()
			self.clicked = False
			# if self.oldPt != []:
			# 	self.undoBuff.append(list(self.points))

			if self.shiftKey:
				temp = [z for z in self.points if (z[0] - x)**2 + (z[1] - y)**2 > (SIZE + SIZE)**2]
				if len(self.points) - len(temp) > 0:
					self.points = [z for z in self.points if (z[0] - x)**2 + (z[1] - y)**2 > (SIZE + SIZE)**2]
				else:
					self.undoBuff = self.undoBuff[:-1]
			else:
				minDist = -1
				index = -1
				if len(self.points) > 0:
					minDist = abs((self.points[0][0] - x)**2 + (self.points[0][1] - y)**2)
					index = 0
					i = 0
					for pt in self.points:
						dist = abs((pt[0] - x)**2 + (pt[1] - y)**2)
						if dist < minDist:
							minDist = dist
							index = i
						i += 1 
					if index > 0 and index < len(self.points) - 1:
						left = abs((self.points[index - 1][0] - x)**2 + (self.points[index - 1][1] - y)**2) 
						right = abs((self.points[index + 1][0] - x)**2 + (self.points[index + 1][1] - y)**2)
						if left < right:
							index -= 1
						elif right < left:
							index += 1
					self.points.insert(index, [x, y])
				else:
					self.points += [[x, y]]
			self.oldPt = []