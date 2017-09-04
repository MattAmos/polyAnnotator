#! python3
#! PY_PYTHON=3

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from frame import Frame


##### MAIN WINDOW CLASS #####
class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.frame = Frame()
		self.initUI()

	def initUI(self):				
		self.setCentralWidget(self.frame) 
		
		exitAct = QAction(QIcon("images/web.png"), '&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setShortcut('Escape')
		exitAct.setStatusTip('Exit Application')
		exitAct.triggered.connect(self.closeEvent)

		self.toolbar = self.addToolBar('Exit')
		self.toolbar.addAction(exitAct)

		menuBar = self.menuBar()
		fileMenu = menuBar.addMenu('File')

		impMenu = QMenu('Import', self)
		impAct = QAction('Import mail', self)
		impMenu.addAction(impAct)

		fileMenu.addMenu(impMenu)
		fileMenu.addAction(exitAct)

		self.setMouseTracking(True)
		screen = QDesktopWidget().screenGeometry()
		self.setGeometry(0, 0, 0.6 * screen.width(), 0.6 * screen.height())
		self.setWindowTitle('Poly Annotator v0.01')
		self.center()
		self.show()

	def center(self):
		'''centers the window on the screen'''
        
		screen = QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

	def keyPressEvent(self, e):
		key = e.key()
		if e.key() == Qt.Key_Escape:
			self.quit()

	def contextMenuEvent(self, event):
		cmenu = QMenu(self)
		saveAct = cmenu.addAction("Save")
		clearAct = cmenu.addAction("Clear")
		quitAct = cmenu.addAction("Quit")
		action = cmenu.exec_(self.mapToGlobal(event.pos()))
		if action == saveAct:
			self.frame.savePoly()
		elif action == clearAct:
			self.frame.clearPoints()
		elif action == quitAct:
			self.closeEvent()

	def closeEvent(self):
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			QCoreApplication.instance().quit()