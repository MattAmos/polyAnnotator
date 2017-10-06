#! python3
#! PY_PYTHON=3

import sys, json
import os.path
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from frame import Frame

##### MAIN WINDOW CLASS #####
class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.dialog = QFileDialog(self)
		self.screen = None
		self.currDir = None
		self.files = None
		self.currImage = None
		self.frame = None
		self.currIndex = 0
		self.polygonPool = []
		self.icon = None
		self.helpList = [
			"Previous frame : ,",
			"Next frame : .",
			"Previous polygon : <-",
			"Next polygon : ->",
			"Reset image : 5",
			"Create new point : M1",
			"Remove point : SHIFT + M1",
			"Delete polygon : DEL",
			"Move image : M3"
		]
		self.helpText = ""
		for d in self.helpList:
			self.helpText += '{:16} \t {:>9}'.format(d[0:d.index(":")], d[d.index(":") + 1:]) + '\n'
		self.helpText = self.helpText[:-1]
		self.initUI()

	def initUI(self):
		self.setCentralWidget(self.frame)
		exitAct = QAction(QIcon("icon/exit.png"), '&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setShortcut('Escape')
		exitAct.setStatusTip('Exit Application')
		exitAct.triggered.connect(self.closeEvent)

		loadDir = QAction(QIcon('icon/load.png'), '&Load', self)
		loadDir.setShortcut('Ctrl+O')
		loadDir.setStatusTip('Load Directory')
		loadDir.triggered.connect(self.loadDir)

		saveDir = QAction(QIcon('icon/save.png'), '&Save', self)
		saveDir.setShortcut('Ctrl+S')
		saveDir.setStatusTip('Save Directory')
		saveDir.triggered.connect(self.writeOutPolygons)

		helpAct = QAction(QIcon('icon/help.png'), '&Controls', self)
		helpAct.setShortcut('Ctrl+H')
		helpAct.setStatusTip('Controls')
		helpAct.triggered.connect(self.showHelp)

		self.toolbar = self.addToolBar('Exit')
		self.toolbar.addAction(exitAct)
		self.toolbar = self.addToolBar('Save')
		self.toolbar.addAction(saveDir)
		self.toolbar = self.addToolBar('Load')
		self.toolbar.addAction(loadDir)
		self.toolbar = self.addToolBar('Controls')
		self.toolbar.addAction(helpAct)

		menuBar = self.menuBar()
		fileMenu = menuBar.addMenu('File')
		helpMenu = menuBar.addMenu('Help')

		fileMenu.addAction(saveDir)
		fileMenu.addAction(loadDir)
		fileMenu.addAction(exitAct)
		helpMenu.addAction(helpAct)

		self.setMouseTracking(True)
		self.screen = QDesktopWidget().screenGeometry()
		if self.currImage is not None and self.frame is not None:
			self.setGeometry(self.screen.x(), self.screen.y(), self.frame.image.width(), self.frame.image.height())
		else:
			self.setGeometry(self.screen.x(), self.screen.y(), 0.6*self.screen.width(), 0.6*self.screen.height())
		self.setWindowTitle('Poly Annotator v0.03')
		pixmap = QPixmap("icon/web.png")
		self.setWindowIcon(QIcon(pixmap))
		self.icon = QIcon(pixmap)
		self.center()
		self.show()

	def center(self):
		'''centers the window on the screen'''
		size = self.geometry()
		self.move((self.screen.width()-size.width())/2, (self.screen.height()-size.height())/2)		

	def keyPressEvent(self, e):
		# ,
		if e.key() == Qt.Key_Comma:
			self.savePoly()
			self.currIndex -= 1
			self.getNewFrame()
		# . 
		elif e.key() == Qt.Key_Period:
			self.savePoly()
			self.currIndex += 1
			self.getNewFrame()
		if self.frame is not None:
			# SHIFT
			if e.key() == Qt.Key_Shift:
				self.frame.shiftKey = True
			# CTRL
			elif e.key() == Qt.Key_Control:
				self.frame.ctrlKey = True
			# 5
			elif e.key() == Qt.Key_5:
				self.frame.setGeometry(self.screen.x(), self.screen.y(), self.frame.image.width(), self.frame.image.height())
			# CTRL + Z
			elif e.key() == Qt.Key_Z and self.frame.ctrlKey:
				print("[DEBUG] TODO: UNDO!")
			# ENTER
			elif e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
				self.frame.addPoly()
				self.savePoly()
				self.writeOutPolygons()
			# <-
			elif e.key() == Qt.Key_Left:
				self.frame.selectPoly(-1)
			# ->
			elif e.key() == Qt.Key_Right:
				self.frame.selectPoly(1)
			elif e.key() == Qt.Key_Delete:
				if len(self.frame.points) > 0: 
					self.frame.clearPoints()
		elif e.key() == Qt.Key_Escape:
			self.quit()

	def keyReleaseEvent(self, e):
		if e.key() == Qt.Key_Escape:
			QCoreApplication.instance().quit()
		if self.frame is not None:
			if e.key() == Qt.Key_Shift:
				self.frame.shiftKey = False
			elif e.key() == Qt.Key_Control:
				self.frame.ctrlKey = False

	def loadDir(self):
		self.currDir = self.dialog.getExistingDirectory(self, 'Select image directory')
		self.files = listdir(self.currDir)
		self.getNewFrame()
	
	def savePoly(self):
		if self.frame is not None and len(self.frame.polygons) > 0:
			index = -1; count = 0
			for p in self.polygonPool:
				if p[0] == self.files[self.currIndex]:
					index = count
					self.polygonPool[count][1] = list(self.frame.polygons)
					break
				count += 1
			if index == -1:
				self.polygonPool.append([self.files[self.currIndex], list(self.frame.polygons)])
			if self.frame.modified:
				self.writeOutPolygons()

	def getNewFrame(self):
		self.currIndex = self.currIndex % len(self.files)		
		self.currImage = QImage(self.currDir + "/" + self.files[self.currIndex])
		self.updateFrame()

	def updateFrame(self):
		if self.files is not None and len(self.files) > 0:
			copyPoly = []
			if self.frame is not None:
				copyPoly = list(self.frame.polygons)
			self.frame = Frame(self, self.currImage)
			if len(self.polygonPool) == 0:
				self.readInPolygons()
			self.setGeometry(self.x(), self.y(), self.frame.image.width(), self.frame.image.height())
			self.show()
			tempPoly = next((z for z in self.polygonPool if z[0] == self.files[self.currIndex]), [])
			if tempPoly != []:
				self.frame.polygons = list(tempPoly[1])
			elif copyPoly != []:
				self.frame.polygons = list(copyPoly)
		else:
			self.frame = None
		self.setCentralWidget(self.frame)
		self.setWindowTitle('Poly Annotator v0.03')
		pixmap = QPixmap("icon/web.png")
		self.setWindowIcon(QIcon(pixmap))

	def showHelp(self):
		msg = QMessageBox()
		msg.setWindowTitle("Controls")
		msg.setText(self.helpText)
		msg.move((self.screen.width() - msg.width())/2, (self.screen.height() - msg.height())/2)		
		msg.exec_()

	def writeOutPolygons(self):
		if(len(self.polygonPool) > 0):
			with open(self.currDir + ".json", 'w') as f:
				json.dump(self.polygonPool, f)
				print("[LOG] Saved polygons from {} frames into {}".format(len(self.polygonPool), self.currDir + ".json"))

	def readInPolygons(self):
		if(os.path.isfile(self.currDir + ".json")):
			with open(self.currDir + ".json", 'r') as f:
				temp = json.load(f)
				if len(temp) > 0:
					self.polygonPool = list(temp)
					print("[LOG] Read polygons data of {} frames from {}".format(len(self.polygonPool), self.currDir + ".json"))

	def closeEvent(self):
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			QCoreApplication.instance().quit()