#! python3
#! PY_PYTHON=3

import sys, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

##### GENERIC WIDGET CLASS #####
class Widget(QFrame):
	def __init__(self):
		super().__init__()
		self.points = []
		self.currPoint = []
		self.shiftKey = False
		self.initUI()

	def initUI(self):
		self.setFocusPolicy(Qt.StrongFocus)
		QToolTip.setFont(QFont('SansSerif', 10))
		self.setToolTip('This is a <b>QWidget</b> widget')

		self.setMouseTracking(True)

		self.center()
		self.setWindowTitle('Message box')
		self.setWindowIcon(QIcon('images/web.png'))
		self.show()

	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)
		self.drawPoints(qp)
		qp.end()
		self.update()

	def drawPoints(self, qp):
		qp.setPen(QPen(Qt.black, 5, Qt.SolidLine))
		size = self.size()

		for i in range(len(self.points)):
			qp.drawPoint(self.points[i][0], self.points[i][1])  

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Shift:
			print("Shift down")
			self.shiftKey = True

	def keyReleaseEvent(self, e):
		if e.key() == Qt.Key_Shift and self.shiftKey:
			print("Shift up")
			self.shiftKey = False
		elif e.key() == Qt.Key_Escape:
			QCoreApplication.instance().quit

	def mouseMoveEvent(self, e):
		x = e.x()
		y = e.y()
		text = "x: {0},  y: {1}".format(x, y)

	def mousePressEvent(self, e):
		x = e.x()
		y = e.y()
		text = "S: x: {0},  y: {1}".format(x, y)
		print(self.points)

	def mouseReleaseEvent(self, e):
		x = e.x()
		y = e.y()
		text = "E: x: {0},  y: {1}".format(x, y)
		
		if self.shiftKey:
			print([z for z in self.points if (z[0] - x)**2 + (z[1] - y)**2 > 100])
			self.points = [z for z in self.points if (z[0] - x)**2 + (z[1] - y)**2 > 100]
		else:
			self.points += [[x, y]]
		print(self.points)