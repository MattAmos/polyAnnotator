import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton, 
	QMessageBox, QDesktopWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QAction, qApp, QMenu, QTextEdit, QGridLayout, QLabel)
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import (QIcon, QFont)

##### GENERIC WIDGET CLASS #####
class Widget(QWidget):
	def __init__(self):
		super().__init__()
		self.imageWidth = 500
		self.imageHeight = 500
		self.initUI()

	def initUI(self):
		QToolTip.setFont(QFont('SansSerif', 10))
		self.setToolTip('This is a <b>QWidget</b> widget')

		btn = QPushButton('Button', self)
		btn.setToolTip('This is a <b>QPushButton</b> widget')
		btn.resize(btn.sizeHint())

		qbtn = QPushButton('Quit', self)
		qbtn.clicked.connect(self.closeEvent)
		qbtn.setToolTip('Click to close')
		qbtn.resize(qbtn.sizeHint())
		
		hbox = QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(btn)
		hbox.addWidget(qbtn)

		self.setLayout(hbox)

		# self.center()
		self.setWindowTitle('Message box')
		self.setWindowIcon(QIcon('images/web.png'))
		self.show()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def closeEvent(self):
		reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			QCoreApplication.instance().quit()

##### MAIN WINDOW CLASS #####
class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.shiftKey = False
		self.initUI()

	def initUI(self):
		grid = QGridLayout()
		grid.setSpacing(10)
		x = 0
		y = 0
		
		self.text = "x: {0},  y: {1}".format(x, y)
		
		self.label = QLabel(self.text, self)
		grid.addWidget(self.label, 0, 0, Qt.AlignTop)
		
		
		self.setLayout(grid)
		
		exitAct = QAction(QIcon("images/web.png"), '&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit Application')
		exitAct.triggered.connect(qApp.quit)

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

		self.setGeometry(0, 0, 1280, 720)
		self.setWindowTitle('Simple Menu')
		self.show()

	def test():
		print ("TEST!")

	def contextMenuEvent(self, event):
		cmenu = QMenu(self)
		newAct = cmenu.addAction("New")
		opnAct = cmenu.addAction("Open")
		quitAct = cmenu.addAction("Quit")
		action = cmenu.exec_(self.mapToGlobal(event.pos()))
		if action == quitAct:
			qApp.quit()

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()
		elif e.key() == Qt.Key_Shift:
			self.shiftKey = True

	def keyReleaseEvent(self, e):
		if self.shiftKey:
			self.shiftKey = False

	def mouseMoveEvent(self, e):
		x = e.x()
		y = e.y()
		text = "x: {0},  y: {1}".format(x, y)
			
		self.label.setText(text)

	def mousePressEvent(self, e):
		x = e.x()
		y = e.y()
		text = "S: x: {0},  y: {1}".format(x, y)
		if self.shiftKey:
			print("**")
		print(text)

	def mouseReleaseEvent(self, e):
		x = e.x()
		y = e.y()
		text = "E: x: {0},  y: {1}".format(x, y)
		if self.shiftKey:
			print("**")
		print(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())