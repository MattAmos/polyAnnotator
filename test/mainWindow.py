#! /usr/bin/env python2

import sys, json
import os.path
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from frame import Frame
import cv2
import numpy as np
import video_pb2

##### MAIN WINDOW CLASS #####
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.screen = None
        self.imageDir = None
        self.jsonDir = None
        self.files = None
        self.currImage = None
        self.frame = None
        self.currIndex = 0
        # Dictionary entires for annotations and frames for reference
        # annoDict  = {'p' : [], 'label' : ''}
        # frameDict = {'annotation' : {}, 'frameNo' : -1}
        self.videoDict = {'frame' : [], 'path' : '', 'width' : -1, 'height' : -1}
        self.polygonPool = []
        self.polygonCount = None
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
        self.capture = None
        self.currVideo = None
        self.useVideo = False
        self.videoFrame = 0
        self.videoNumFrames = None
        self.imageCount = None

        self.poly_video = None
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

        loadVideo = QAction(QIcon('Load video'), '&Load', self)
        loadVideo.setShortcut('Ctrl+L')
        loadVideo.setStatusTip('Load video')
        loadVideo.triggered.connect(self.loadVideo)

        loadJSONDir = QAction(QIcon('Set labels directory'), '&Labels', self)
        loadJSONDir.setShortcut('Ctrl+J')
        loadJSONDir.setStatusTip('Set load/save directory for image labels')
        loadJSONDir.triggered.connect(self.setJSONDir)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAct)
        self.toolbar = self.addToolBar('Save')
        self.toolbar.addAction(saveDir)
        self.toolbar = self.addToolBar('Load')
        self.toolbar.addAction(loadDir)
        self.toolbar = self.addToolBar('Controls')
        self.toolbar.addAction(helpAct)
        self.toolbar = self.addToolBar('Load')
        self.toolbar.addAction(loadVideo)
        self.toolbar = self.addToolBar('Set labels directory')
        self.toolbar.addAction(loadJSONDir)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')
        helpMenu = menuBar.addMenu('Help')

        fileMenu.addAction(saveDir)
        fileMenu.addAction(loadDir)
        fileMenu.addAction(loadVideo)
        fileMenu.addAction(loadJSONDir)
        fileMenu.addAction(exitAct)
        helpMenu.addAction(helpAct)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.imageCount = QLabel('No images loaded', self.statusBar)
        self.statusBar.addPermanentWidget(self.imageCount)
        self.polygonCount = QLabel('No polygons loaded', self.statusBar)
        self.statusBar.addPermanentWidget(self.polygonCount)

        self.setMouseTracking(True)
        self.setScreenGeometry()

        self.setWindowTitle('Poly Annotator v0.03')
        pixmap = QPixmap("icon/web.png")
        self.setWindowIcon(QIcon(pixmap))
        self.icon = QIcon(pixmap)
        self.center()
        self.show()

    def center(self):
        size = self.geometry()
        self.move((self.screen.width()-size.width())/2, (self.screen.height()-size.height())/2)

    def keyPressEvent(self, e):
        modifiers = e.modifiers()
        # ,
        if e.key() == Qt.Key_Comma:
            self.savePoly()
            if self.useVideo:
                self.writeOutPolygons()
                if e.modifiers() == Qt.ControlModifier:
                    video = os.path.splitext(os.path.basename(self.currVideo))[0]
                    jsonFiles = sorted([int(os.path.splitext(os.path.basename(f))[0].replace('{0}_'.format(video), ''))
                        for f in os.listdir(self.jsonDir) if f.endswith('.json') and os.path.basename(f).startswith(video)], reverse=True)
                    self.videoFrame = next(v for i, v in enumerate(jsonFiles) if v < self.videoFrame)
                else:
                    self.videoFrame -= 1
            else:
                self.currIndex -= 1
            if self.videoFrame is not None and self.videoNumFrames is not None:
                self.videoFrame = max(0, min(self.videoFrame, self.videoNumFrames))
            self.getNewFrame()
        # .
        elif e.key() == Qt.Key_Period:
            self.savePoly()
            if self.useVideo:
                self.writeOutPolygons()
                if e.modifiers() == Qt.ControlModifier:
                    video = os.path.splitext(os.path.basename(self.currVideo))[0]
                    jsonFiles = sorted([int(os.path.splitext(os.path.basename(f))[0].replace('{0}_'.format(video), ''))
                        for f in os.listdir(self.jsonDir) if f.endswith('.json') and os.path.basename(f).startswith(video)])
                    self.videoFrame = next(v for i, v in enumerate(jsonFiles) if v > self.videoFrame)
                else:
                    self.videoFrame += 1
            else:
                self.currIndex += 1
            if self.videoFrame is not None and self.videoNumFrames is not None:
                self.videoFrame = max(0, min(self.videoFrame, self.videoNumFrames))
            self.getNewFrame()
        if self.frame is not None:
            # SHIFT
            if e.key() == Qt.Key_Shift:
                self.frame.keys.SHIFT = True
            # CTRL
            if e.key() == Qt.Key_Control:
                self.frame.keys.CTRL = True
            # ALT
            if e.key() == Qt.Key_Alt:
                self.frame.keys.ALT = True

            # 5
            if e.key() == Qt.Key_5:
                self.frame.setGeometry(self.screen.x(), self.screen.y(), self.frame.image.width(), self.frame.image.height())
            # CTRL + Z
            elif e.key() == Qt.Key_Z and self.frame.ctrlKey:
                self.statusBar.showMessage('I don\'t know how to undo yet!')
            # ENTER
            elif e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
                self.frame.addPoly()
                self.savePoly()
                self.writeOutPolygons()
                self.statusBar.showMessage('Added new polygon')
            # <-
            elif e.key() == Qt.Key_Left:
                self.frame.selectPoly(-1)
            # ->
            elif e.key() == Qt.Key_Right:
                self.frame.selectPoly(1)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.closeEvent()
        if self.frame is not None:
            if e.key() == Qt.Key_Shift:
                self.frame.keys.SHIFT = False
            if e.key() == Qt.Key_Control:
                self.frame.keys.CTRL = False
            if e.key() == Qt.Key_Alt:
                self.frame.keys.ALT = False

            if e.key() == Qt.Key_Delete:
                if len(self.frame.points) > 0:
                    self.frame.clearPoints()
                    self.savePoly()
                    self.statusBar.showMessage('Deleted polygon')

    def loadDir(self):
        if self.useVideo and self.capture and self.capture.isOpened():
            self.capture.release()

        self.statusBar.showMessage('Loading an image directory')
        self.useVideo = False
        self.imageDir = QFileDialog.getExistingDirectory(self, 'Select image directory')

        if self.jsonDir is None:
            self.jsonDir = self.imageDir

        if self.imageDir is not '':
            self.files = listdir(self.imageDir)
            self.getNewFrame()
            self.statusBar.showMessage('Image directory successfully loaded')

    def loadVideo(self):
        if self.capture and self.capture.isOpened():
            self.capture.release()

        self.statusBar.showMessage('Loading a video')
        self.currVideo, filter = QFileDialog.getOpenFileName(self, 'Select video')
        if os.path.isfile(self.currVideo):
            self.imageDir = os.path.dirname(os.path.abspath(self.currVideo))

            if self.jsonDir is None:
                self.jsonDir = self.imageDir

            self.capture = cv2.VideoCapture(self.currVideo)

            if self.capture.isOpened() == False:
                print('Failed to open video file "{}"'.format(self.currVideo))
                self.currVideo = None
                self.useVideo = False
                return

            self.useVideo = True
            self.currIndex = 0
            self.files = [self.currVideo]
            self.videoFrame = 0
            self.videoNumFrames = int(self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
            self.getNewFrame()
            self.statusBar.showMessage('Video successfully loaded')

    def setJSONDir(self):
        self.jsonDir = QFileDialog.getExistingDirectory(self, 'Select labels directory')

    def savePoly(self):
        if self.frame is not None:
            if len(self.frame.frameDict["annotation"]) > 0:
                index = -1
                count = 0
                for p in self.polygonPool:
                    if p[0] == self.files[self.currIndex]:
                        index = count
                        self.polygonPool[count][2] = list(self.frame.frameDict["annotation"])
                        break
                    count += 1
                if index == -1:
                    print("TODO: Handle this case!")
                    self.polygonPool.append([self.files[self.currIndex], self.videoFrame if self.useVideo else 0, list(self.frame.frameDict["annotation"])])
            else:
                index = -1
                count = 0
                for p in self.polygonPool:
                    if p[0] == self.files[self.currIndex]:
                        index = count
                        self.polygonPool[count][2] = []
                        break
                    count += 1

            if self.frame.modified:
                self.writeOutPolygons()

        self.polygonCount.setText('{0} polygons in image'.format(len(self.frame.frameDict["annotation"])))

    def getNewFrame(self):
        if self.useVideo and self.capture.isOpened():
            self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, self.videoFrame)
            ret, frame = self.capture.read()

            if ret:
                height, width, byteValue = frame.shape
                byteValue = byteValue * width
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
                self.currImage = QImage(frame, width, height, byteValue, QImage.Format_RGB888)

            else:
                return

        else:
            self.currIndex = self.currIndex % len(self.files)
            self.currImage = QImage(self.imageDir + "/" + self.files[self.currIndex])

        self.imageCount.setText('Processing image {0}/{1}'.format(self.videoFrame if self.useVideo else self.currIndex,
                self.videoNumFrames if self.useVideo else len(self.files)))
        self.updateFrame()

    def updateFrame(self):
        if self.useVideo or (self.files is not None and len(self.files) > 0):
            copyFrame = {}
            if self.frame is not None:
                copyFrame = self.frame.frameDict
            self.frame = Frame(self, self.currImage)
            if len(self.videoDict["frame"]) == 0 or self.useVideo:
                self.readInPolygons()

            self.setScreenGeometry()
            self.show()

            tempFrame = {}

            for i in range(0, len(self.videoDict["frame"])): # each frame
                if('{0:015d}.{1}'.format(self.videoDict["frame"][i]["frameNo"], "JPG") == self.files[self.currIndex]):
                    tempFrame = self.videoDict["frame"][i]
                    break

            if tempFrame != {}:
                self.statusBar.showMessage('Frame loaded from file')
                self.frame.frameDict = tempFrame
            elif copyFrame != {}:
                self.statusBar.showMessage('Frame copied from previous frame')
                tempFrameNo = copyFrame["frameNo"]
                self.frame.frameDict = copyFrame
                copyFrame["frameNo"] = tempFrameNo
            if self.frame.frameDict != {}:
                self.polygonCount.setText('{0} polygons in image'.format(len(self.frame.frameDict["annotation"])))
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
        if(len(self.videoDict) > 0):
            if self.useVideo:
                outputFile = os.path.join(self.jsonDir, os.path.basename(self.files[self.currIndex]))
                outputFile = '{0}_{1:015d}.{2}'.format(os.path.splitext(outputFile)[0], self.videoFrame, "json")
            else:
                outputFile = os.path.join(self.jsonDir, os.path.basename(self.files[self.currIndex]))
                outputFile = '{0}.{1}'.format(os.path.splitext(outputFile)[0], "json")

            with open(outputFile, 'w') as f:
                json.dump(self.videoDict, f)

            self.statusBar.showMessage('Successfully saved {0} frames to file {1}'.format(len(self.videoDict["frame"]), outputFile))

    def readInPolygons(self):
        # self.protoReadInPolygons()

        if self.useVideo:
            inputFile = os.path.join(self.jsonDir, os.path.basename(self.files[self.currIndex]))
            inputFile = '{0}_{1:015d}.{2}'.format(os.path.splitext(inputFile)[0], self.videoFrame, "json")
        else:
            inputFile = os.path.join(self.jsonDir, os.path.basename(self.files[self.currIndex]))
            inputFile = '{0}.{1}'.format(self.jsonDir, "json")
        print('{}'.format(inputFile));
        if(os.path.isfile(inputFile)):
            with open(inputFile, 'r') as f:
                temp = json.load(f)
                if len(temp) > 0:
                    # self.printVideoDict(temp)
                    # print(temp["frame"])
                    self.videoDict = temp

            self.statusBar.showMessage('Successfully loaded {0} frames from file {1}'.format(len(self.videoDict["frame"]), inputFile))

    def printVideoDict(self, temp):
        print('{0}, {1}x{2}'.format(temp["path"], temp["width"], temp["height"]))
        for i in range(0, len(temp["frame"])):
            print('FrameNo: {0}'.format(temp["frame"][i]["frameNo"]))
            for j in range(0, len(temp["frame"][i]["annotation"])):
                print('\tAnnotation: {0}'.format(temp["frame"][i]["annotation"][j]["label"]))
                for k in range(0, len(temp["frame"][i]["annotation"][j]["p"])):
                    print('\t\t{0}, {1}'.format(temp["frame"][i]["annotation"][j]["p"][k]["x"], temp["frame"][i]["annotation"][j]["p"][k]["y"]))
        # print(temp["frame"])

    def protoReadInPolygons(self):
        # Instead of self.jsonDir we want to read in {VIDEO FILENAME}.proto and the images from {VIDEO FILENAME}
        print('{}.{}'.format(self.jsonDir, "proto"))
        inputFile = '{0}.{1}'.format(self.jsonDir, "proto")
        
        if(os.path.isfile(inputFile)):
            with open(inputFile, 'r') as f:
                self.poly_video = video_pb2.Video()
                self.poly_video.ParseFromString(f.read())

            f.close()
            print('{}'.format(self.poly_video.__str__()))


    def closeEvent(self):
        reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.useVideo:
                self.capture.release()

            QCoreApplication.instance().quit()

    def setScreenGeometry(self):
        self.screen = QDesktopWidget().availableGeometry()
        width = 0.6 * self.screen.width()
        height = 0.6 * self.screen.height()

        if self.currImage is not None and self.frame is not None:
            width = self.frame.image.width() if self.frame.image.width() < (0.9 * self.screen.width()) else self.screen.width()
            height = self.frame.image.height() if self.frame.image.height() < (0.9 * self.screen.height()) else self.screen.height()

        self.setGeometry(self.screen.x(), self.screen.y(), width, height)
