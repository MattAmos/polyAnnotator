#! python3
#! PY_PYTHON=3

import sys
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
		self.currDir = None
		self.files = None
		self.currImage = None
		self.frame = None
		self.currIndex = 0
		self.polygonPool = []
		self.initUI()

	def initUI(self):
		self.setCentralWidget(self.frame)
		exitAct = QAction(QIcon("images/web.png"), '&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setShortcut('Escape')
		exitAct.setStatusTip('Exit Application')
		exitAct.triggered.connect(self.closeEvent)

		loadDir = QAction(QIcon('Import directory'), '&Import', self)
		loadDir.setShortcut('Ctrl+O')
		loadDir.setStatusTip('Import Directory')
		loadDir.triggered.connect(self.loadDir)

		self.toolbar = self.addToolBar('Exit')
		self.toolbar.addAction(exitAct)
		self.toolbar = self.addToolBar('Import')
		self.toolbar.addAction(loadDir)

		menuBar = self.menuBar()
		fileMenu = menuBar.addMenu('File')

		fileMenu.addAction(loadDir)
		fileMenu.addAction(exitAct)

		self.setMouseTracking(True)
		screen = QDesktopWidget().screenGeometry()
		if self.currImage is not None and self.frame is not None:
			self.setGeometry(0, 0, self.frame.image.width(), self.frame.image.height())
		else:
			screen = QDesktopWidget().screenGeometry()
			self.setGeometry(0, 0, 0.6*screen.width(), 0.6*screen.height())
		
		self.setWindowTitle('Poly Annotator v0.01')
		pixmap = QPixmap("icon/web.png")
		self.setWindowIcon(QIcon(pixmap))

		self.center()
		self.show()

	def center(self):
		'''centers the window on the screen'''
		screen = QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)		

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Shift:
			print("Shift down")
			self.frame.shiftKey = True
		elif e.key() == Qt.Key_Control:
			self.frame.ctrlKey = True
		elif e.key() == Qt.Key_Comma:
			self.savePoly()
			self.currIndex -= 1
			self.getNewFrame()
		elif e.key() == Qt.Key_Period:
			self.savePoly()
			self.currIndex += 1
			self.getNewFrame()
		if self.frame is not None:
			# CTRL + Z
			if e.key() == Qt.Key_Z and self.frame.ctrlKey:
				if len(self.frame.undoBuff) > 0:
					self.frame.points = self.frame.undoBuff[-1]
					self.frame.undoBuff = self.frame.undoBuff[:-1]
			# ENTER
			elif e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
				self.frame.addPoly()
			# <-
			elif e.key() == Qt.Key_Left:
				self.frame.selectPoly(-1)
			# ->
			elif e.key() == Qt.Key_Right:
				self.frame.selectPoly(1)
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
			elif e.key() == Qt.Key_Delete:
				if len(self.frame.points) > 0: 
					self.frame.undoBuff.append(list(self.frame.points))
					self.frame.clearPoints()

	def loadDir(self):
		self.currDir = self.dialog.getExistingDirectory(self, 'Select image directory')
		self.files = listdir(self.currDir)
		self.getNewFrame()
	
	def savePoly(self):
		if self.frame is not None and len(self.frame.polygons) > 0:
			index = -1
			count = 0
			for p in self.polygonPool:
				if p[0] == self.files[self.currIndex]:
					index = count
					self.polygonPool[count][1] = list(self.frame.polygons)
					break
				count += 1
			if index == -1:
				self.polygonPool.append([self.files[self.currIndex], list(self.frame.polygons)])

	def getNewFrame(self):
		self.currIndex = self.currIndex % len(self.files)		
		self.currImage = QImage(self.currDir + "/" + self.files[self.currIndex])
		self.updateFrame()

	def updateFrame(self):
		if self.files is not None and len(self.files) > 0:
			self.frame = Frame(self, self.currImage)
			self.setGeometry(0, 0, self.frame.image.width(), self.frame.image.height())
			self.show()
			tempPoly = next((z for z in self.polygonPool if z[0] == self.files[self.currIndex]), [])
			if(tempPoly != []):
				print("{0} -> {1}".format(self.files[self.currIndex], tempPoly))
				self.frame.polygons = list(tempPoly[1])
		else:
			self.frame = None
		self.setCentralWidget(self.frame)
		self.setWindowTitle('Poly Annotator v0.01')
		pixmap = QPixmap("icon/web.png")
		self.setWindowIcon(QIcon(pixmap))

	def contextMenuEvent(self, event):
		cmenu = QMenu(self)
		saveAct = cmenu.addAction("Save")
		clearAct = cmenu.addAction("Clear")
		quitAct = cmenu.addAction("Quit")
		action = cmenu.exec_(self.mapToGlobal(event.pos()))
		if self.frame is not None:
			if action == saveAct:
				self.frame.addPoly()
			elif action == clearAct:
				self.frame.clearPoints()
		elif action == quitAct:
			self.closeEvent()

	def closeEvent(self):
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			QCoreApplication.instance().quit()