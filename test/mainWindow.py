#! python3
#! PY_PYTHON=3

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from widget import Widget


##### MAIN WINDOW CLASS #####
class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.widget = Widget()
		self.initUI()

	def initUI(self):				
		self.setCentralWidget(self.widget) 
		
		exitAct = QAction(QIcon("images/web.png"), '&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
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


		self.setGeometry(0, 0, 1280, 720)
		self.setWindowTitle('Simple Menu')
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
		newAct = cmenu.addAction("New")
		opnAct = cmenu.addAction("Open")
		quitAct = cmenu.addAction("Quit")
		action = cmenu.exec_(self.mapToGlobal(event.pos()))
		if action == quitAct:
			self.closeEvent

	def closeEvent(self):
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			QCoreApplication.instance().quit()