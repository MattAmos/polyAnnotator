#! python3
#! PY_PYTHON=3

import sys, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

SIZE = 5
UNDO_SIZE = 20

##### GENERIC FRAME CLASS #####
class Frame(QFrame):
	def __init__(self):
		super().__init__()
		# Containers
		self.points = []
		self.polygons = []
		self.undoBuff = []
		self.currPoint = []
		# Key variables
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
		self.setWindowTitle('Image Segmentation')
		pixmap = QPixmap("icon/web.png")
		self.setWindowIcon(QIcon(pixmap))
		self.show()

	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)
		self.drawBrushes(qp)
		self.drawPoints(qp)
		qp.end()
		self.update()

	def getQPoints(self):
		qPoints = []
		for i in range(len(self.points)):
			qPoints += [QPoint(self.points[i][0], self.points[i][1])]  
		return qPoints

	def savePoly(self):
		print("saved!")

	def clearPoints(self):
		self.points = []

	### Drawing Functions ###

	def drawPoints(self, qp):
		qp.setPen(QPen(Qt.black, SIZE, Qt.SolidLine))
		size = self.size()
		qPoints = self.getQPoints()
		for pt in self.points:
			qp.drawEllipse(pt[0], pt[1], SIZE, SIZE)
		qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
		qp.drawPolygon(QPolygon(qPoints))

	def drawBrushes(self, qp):
		img = QImage("web.jpg")
		# brush = QBrush(Qt.SolidPattern)
		# brush.setTextureImage(img)
		qp.drawImage(QPoint(0,0), img)


		brush = QBrush(Qt.SolidPattern)
		qPoints = self.getQPoints() 
		brush.setColor(QColor(0, 255, 255, 240))
		qp.drawPolygon(QPolygon(qPoints))


	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Shift:
			print("Shift down")
			self.shiftKey = True
		elif e.key() == Qt.Key_Z and self.ctrlKey:
			if len(self.undoBuff) > 0:
				self.points = self.undoBuff[-1]
				self.undoBuff = self.undoBuff[:-1]
		elif e.key() == Qt.Key_Control:
			self.ctrlKey = True

	def keyReleaseEvent(self, e):
		if e.key() == Qt.Key_Shift:
			self.shiftKey = False
		elif e.key() == Qt.Key_Control:
			self.ctrlKey = False
		elif e.key() == Qt.Key_Delete:
			self.undoBuff.append(list(self.points))
			self.points = []
		elif e.key() == Qt.Key_Escape:
			QCoreApplication.instance().quit

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
		self.update()

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
			if self.oldPt != []:
				self.undoBuff.append(list(self.points))

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
					minDist = (self.points[0][0] - x)**2 + (self.points[0][1] - y)**2
					index = 0
					i = 0
					for pt in self.points:
						dist = (pt[0] - x)**2 + (pt[1] - y)**2
						if dist < minDist:
							minDist = dist
							index = i
						i += 1 
					self.points.insert(index + 1, [x, y])
				else:
					self.points += [[x, y]]
			self.oldPt = []
			print(len(self.points))
			print(len(self.undoBuff))