#! /usr/bin/env python

import sys, json
import os.path
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from frame import Frame
from copy import deepcopy
import cv2
import numpy as np
import video_pb2

## Dictionary entires for annotations and frames for reference
#   videoDict = {'path' : '', 'width' : -1, 'height' : -1, 'frame' : []}
#   frameDict = {'annotation' : [], 'frameNo' : -1}
#   annoDict  = {'p' : [], 'label' : ''}
#   pointDict = {'x' : -1, 'y' : -1}

DIFF_THRESH = 30

##### MAIN WINDOW CLASS #####
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.dimensions = [0,0]
        self.screen     = None
        self.imageDir   = None
        self.jsonDir    = None
        self.files      = None
        self.currImage  = None
        self.frame      = None
        self.icon       = None
        self.capture    = None
        self.currVideo  = None
        self.imageCount = None
        self.videoNumFrames = None
        self.polygonCount = None
        self.currIndex  = 0
        self.videoFrame = 0

        self.videoDict = {'frame' : [], 'path' : '', 'width' : -1, 'height' : -1}
        self.useVideo = False
        self.polygonPool = []
        self.copiedPolys = []

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

        loadVideo = QAction(QIcon('icon/load.png'), '&Load', self)
        loadVideo.setShortcut('Ctrl+L')
        loadVideo.setStatusTip('Load video')
        loadVideo.triggered.connect(self.loadVideo)

        loadJSONDir = QAction(QIcon('Set labels directory'), '&Labels', self)
        loadJSONDir.setShortcut('Ctrl+J')
        loadJSONDir.setStatusTip('Set load/save directory for image labels')
        loadJSONDir.triggered.connect(self.setJSONDir)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)
        toolbar = self.addToolBar('Save')
        toolbar.addAction(saveDir)
        toolbar = self.addToolBar('Load')
        toolbar.addAction(loadDir)
        toolbar = self.addToolBar('Controls')
        toolbar.addAction(helpAct)
        toolbar = self.addToolBar('Load')
        toolbar.addAction(loadVideo)
        toolbar = self.addToolBar('Set labels directory')
        toolbar.addAction(loadJSONDir)

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

        self.setWindowTitle('Poly Annotator v0.04')
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
        # , or .
        if e.key() == Qt.Key_Comma or e.key() == Qt.Key_Period:
            moveDir = 1
            if e.key() == Qt.Key_Comma : moveDir = -1
            else :  moveDir = 1
            self.savePoly()
            if self.useVideo:
                self.writeOutPolygons()
                if e.modifiers() == Qt.ControlModifier:
                    video = os.path.splitext(os.path.basename(self.currVideo))[0]
                    jsonFiles = sorted([int(os.path.splitext(os.path.basename(f))[0].replace('{0}_'.format(video), ''))
                        for f in os.listdir(self.jsonDir) if f.endswith('.json') and os.path.basename(f).startswith(video)], reverse=True)
                    self.videoFrame = next(v for i, v in enumerate(jsonFiles) if v < self.videoFrame)
                else:
                    self.videoFrame += moveDir
            else:
                self.currIndex += moveDir
            self.currIndex = self.currIndex % len(self.files)
            self.imageCount.setText('Processing image {0}/{1}'.format(self.videoFrame if self.useVideo else self.currIndex,
                self.videoNumFrames if self.useVideo else len(self.files)))
        if self.frame is not None:
            # SHIFT
            if e.key() == Qt.Key_Shift:   self.frame.keys.SHIFT = True
            # CTRL
            if e.key() == Qt.Key_Control: self.frame.keys.CTRL  = True
            # ALT
            if e.key() == Qt.Key_Alt:     self.frame.keys.ALT   = True

            # 5
            if e.key() == Qt.Key_5:
                self.frame.setGeometry(self.screen.x(), self.screen.y(), self.frame.image.width(), self.frame.image.height())
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
            # CTRL + C
            elif e.key() == Qt.Key_C and self.frame.keys.CTRL:
                self.copiedPolys = deepcopy(self.frame.frameDict["annotation"])
                self.statusBar.showMessage('Copied {0} polygons'.format(len(self.frame.frameDict["annotation"])))
            # CTRL + V
            elif e.key() == Qt.Key_V and self.frame.keys.CTRL and self.copiedPolys != []:
                if "annotation" in self.frame.frameDict:
                    self.frame.frameDict["annotation"] += deepcopy(self.copiedPolys)
                else:
                    self.frame.frameDict["annotation"] = deepcopy(self.copiedPolys)
                self.statusBar.showMessage('Pasted {0} polygons'.format(len(self.copiedPolys)))
            # CTRL + Z
            elif e.key() == Qt.Key_Z and self.frame.keys.CTRL:
                self.statusBar.showMessage('I don\'t know how to undo yet!')
            elif e.key() == Qt.Key_Delete and self.frame.keys.CTRL:
                if "annotation" in self.frame.frameDict:
                    self.statusBar.showMessage('Deleted {0} polygons'.format(len(self.frame.frameDict["annotation"])))
                    self.frame.frameDict["annotation"] = []
                else:
                    self.statusBar.showMessage('Deleted 0 polygons')
            elif e.key() == Qt.Key_F:
                numCopies = 1
                while numCopies > 0:
                    numCopies = 0
                    prevFrame = None; prevImage = None
                    currFrame = None; currImage = None
                    for i in range(0, len(self.videoDict["frame"])): # each frame
                        if('{0:010d}.{1}'.format(self.videoDict["frame"][i]["frameNo"], "JPG") == self.files[self.currIndex]):
                                # print('Found current {0}'.format(self.files[self.currIndex]))
                                currFrame = self.videoDict["frame"][i]
                                currImage = cv2.imread('{0}/{1}'.format(self.jsonDir, self.files[self.currIndex]), 0)
                                # print(currImage)

                        if self.currIndex >= 1 and ('{0:010d}.{1}'.format(self.videoDict["frame"][i]["frameNo"], "JPG") == self.files[self.currIndex - 1]):
                                # print('Found previous {0}'.format(self.files[self.currIndex - 1]))
                                prevFrame = self.videoDict["frame"][i]
                                prevImage = cv2.imread('{0}/{1}'.format(self.jsonDir, self.files[self.currIndex - 1]), 0)
                                # print(prevImage)

                        if prevFrame is not None and currFrame is not None:
                            break

                    if prevFrame is not None and prevImage is not None and currFrame is not None and currImage is not None:
                        numCopies = self.opticalFlow(prevFrame, prevImage, currFrame, currImage)
                        print(numCopies)
                        if numCopies > 0:
                            self.currIndex += 1
                            self.currIndex = self.currIndex % len(self.files)
                    else: print('something is none!')

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.currIndex = self.currIndex % len(self.files)
            self.closeEvent()
        if e.key() == Qt.Key_Comma or e.key() == Qt.Key_Period:
            if not e.isAutoRepeat():
                if self.videoFrame is not None and self.videoNumFrames is not None:
                    self.videoFrame = max(0, min(self.videoFrame, self.videoNumFrames))
                self.getNewFrame()
        if self.frame is not None:
            # SHIFT
            if e.key() == Qt.Key_Shift:   self.frame.keys.SHIFT = False
            # CTRL
            if e.key() == Qt.Key_Control: self.frame.keys.CTRL  = False
            # ALT
            if e.key() == Qt.Key_Alt:     self.frame.keys.ALT   = False
            # DEL
            if e.key() == Qt.Key_Delete:
                if self.frame.frameDict != {} and "annotation" in self.frame.frameDict and len(self.frame.frameDict["annotation"]) > 0 and len(self.frame.points) > 0:
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
            self.files.sort()
            self.getNewFrame()
            self.statusBar.showMessage('Image directory successfully loaded')
        else:
            self.jsonDir = None 

    def loadVideo(self):
        if self.capture and self.capture.isOpened():
            self.capture.release()

        self.statusBar.showMessage('Loading a video')
        self.currVideo, filter = QFileDialog.getOpenFileName(self, 'Select video')
        if os.path.isfile(self.currVideo):
            self.imageDir = os.path.dirname(os.path.abspath(self.currVideo))

            if self.jsonDir is None:
                self.jsonDir = self.imageDir

            print(self.currVideo)
            self.capture = cv2.VideoCapture(self.currVideo)

            if self.capture.isOpened() == False:
                print('Failed to open video file "{}"'.format(self.currVideo))
                self.currVideo = None
                self.useVideo = False
                return

            self.useVideo = True
            self.currIndex = 0
            self.files = [self.currVideo]
            self.files.sort()
            self.videoFrame = 0
            self.videoNumFrames = int(self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
            self.getNewFrame()
            self.statusBar.showMessage('Video successfully loaded')

    def setJSONDir(self):
        self.jsonDir = QFileDialog.getExistingDirectory(self, 'Select labels directory')
        if os.path.isfile(self.jsonDir):
            print('is a file!')
        else:
            self.videoDict = {'path' : self.jsonDir, 'width' : -1, 'height' : -1, 'frame' : []}


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
            # copyFrame = {}
            # if self.frame is not None:
            #     copyFrame = self.frame.frameDict
            tempKeys = None
            if self.frame is not None:
                tempKeys = self.frame.keys

            self.frame = Frame(self, self.currImage)
            if tempKeys is not None:
                self.frame.keys = tempKeys
            if len(self.videoDict["frame"]) == 0 or self.useVideo:
                self.readInPolygons()

            # self.show()
            self.setScreenGeometry()

            tempFrame = {}
            for i in range(0, len(self.videoDict["frame"])): # each frame
                if('{0:010d}.{1}'.format(self.videoDict["frame"][i]["frameNo"], "JPG") == self.files[self.currIndex]):
                    tempFrame = self.videoDict["frame"][i]
                    break
                # print('{0}, {1}'.format('{0:010d}.{1}'.format(self.videoDict["frame"][i]["frameNo"], "JPG"), self.files[self.currIndex]))

            if tempFrame != {}:
                self.statusBar.showMessage('Frame loaded from file')
                self.frame.frameDict = tempFrame
            else:
                self.frame.frameDict = {"annotation" : [], "frameNo" : int(self.files[self.currIndex][:-4])}

            if self.frame.frameDict != {}:
                if "annotation" in self.frame.frameDict:
                    self.polygonCount.setText('{0} polygons in image'.format(len(self.frame.frameDict["annotation"])))
                else:
                    self.polygonCount.setText('0 polygons in image')
        else:
            self.frame = None

        self.setCentralWidget(self.frame)

    def opticalFlow(self, prevFrame, prevImage, currFrame, currImage):
        numCopies = 0
        for anno in prevFrame['annotation']:
            if 'p' in anno:
                tempAnno = {'p' : [], 'label' : 'track'}
                for p in anno['p']:
                    if p['x'] + 1 < prevImage.shape[1] and p['x'] - 1 > 0 and p['y'] + 1 < prevImage.shape[0] and p['y'] - 1 > 0:
                        diffScore = 0
                        for x in range(-1, 1):
                            for y in range(-1, 1):
                                print('Curr: {0}'.format(currImage[int(p['y'] + y), int(p['x'] + x)]))
                                print('Prev: {0}'.format(prevImage[int(p['y'] + y), int(p['x'] + x)]))

                                diffScore += abs(int(currImage[int(p['y'] + y), int(p['x'] + x)]) - int(prevImage[int(p['y'] + y), int(p['x'] + x)]))
                        print('diffScore: {0}'.format(diffScore))
                        if diffScore < DIFF_THRESH:
                            tempAnno['p'].append({'x' : p['x'], 'y' : p['y']})
                            numCopies += 1
                    else:
                        tempAnno['p'].append({'x' : p['x'], 'y' : p['y']})
                if len(tempAnno['p'] > 0):
                    currFrame['annotation'].append(deepcopy(tempAnno))
        print(numCopies)
        return numCopies

    def savePoly(self):
        if self.frame is not None:
            if "annotation" in self.frame.frameDict and len(self.frame.frameDict["annotation"]) > 0:
                found = False
                for i in range(0, len(self.videoDict["frame"])): # each frame
                    if('{0:010d}.{1}'.format(self.videoDict["frame"][i]["frameNo"], "JPG") == self.files[self.currIndex]):
                        self.videoDict["frame"][i] = self.frame.frameDict
                        found = True
                        break
                if found == False:
                    self.videoDict["frame"].append({"annotation" : [], "frameNo" : int(self.files[self.currIndex][:-4])})
                self.polygonCount.setText('{0} polygons in image'.format(len(self.frame.frameDict["annotation"])))

                if self.frame.modified:
                    self.writeOutPolygons()
            else:
                found = False
                for i in range(0, len(self.videoDict["frame"])): # each frame
                    if('{0:010d}.{1}'.format(self.videoDict["frame"][i]["frameNo"], "JPG") == self.files[self.currIndex]):
                        self.frame.frameDict.update({'annotation' : [{'label' : 'track', 'p' : self.frame.points}]}) #TODO: Make classes configurable
                        found = True
                        break
                if found == False:
                    self.videoDict["frame"].append({"annotation" : [], "frameNo" : int(self.files[self.currIndex][:-4])})
                self.frame.frameDict.update({'annotation' : []})
        else:
            print('Frame not initialised!')

    def writeOutPolygons(self):
        if self.useVideo:
            outputFile = os.path.join(self.jsonDir, os.path.basename(self.files[self.currIndex]))
            outputFile = '{0}_{1:010d}.{2}'.format(os.path.splitext(outputFile)[0], self.videoFrame, "json")
        else:
            outputFile = os.path.join(self.jsonDir, os.path.basename(self.files[self.currIndex]))
            outputFile = '{0}.{1}'.format(self.jsonDir, "json")

        with open(outputFile, 'w') as f:
            json.dump(self.videoDict, f)

        self.statusBar.showMessage('Successfully saved {0} frames to file {1}'.format(len(self.videoDict["frame"]), outputFile))

    def readInPolygons(self):
        # self.protoReadInPolygons()

        if self.useVideo:
            inputFile = os.path.join(self.jsonDir, os.path.basename(self.files[self.currIndex]))
            inputFile = '{0}_{1:010d}.{2}'.format(os.path.splitext(inputFile)[0], self.videoFrame, "json")
        else:
            inputFile = os.path.join(self.jsonDir, os.path.basename(self.files[self.currIndex]))
            inputFile = '{0}.{1}'.format(self.jsonDir, "json")
        print('INPUT FILE: {}'.format(inputFile));
        if(os.path.isfile(inputFile)):
            with open(inputFile, 'r') as f:
                temp = json.load(f)
                if len(temp) > 0:
                    # self.printVideoDict(temp)
                    # print(temp["frame"])
                    self.videoDict = temp
                else:
                    self.jsonDir = ''

            self.statusBar.showMessage('Successfully loaded {0} frames from file {1}'.format(len(self.videoDict["frame"]), inputFile))


    ### Print Functions ###

    def printAnno(self, anno):
        if "label" in anno and "p" in anno:
            print('\tAnnotation: {0}'.format(anno["label"]))
            for k in range(0, len(anno["p"])):
                print('\t\t{0}, {1}'.format(anno["p"][k]["x"], anno["p"][k]["y"]))

    def printFrame(self, frame):
        if "frameNo" in frame and "annotation" in frame:
            print('FrameNo: {0}'.format(frame["frameNo"]))
            for j in range(0, len(frame["annotation"])):
                self.printAnno(frame["annotation"][j])

    def printVideoDict(self, temp):
        if "path" in temp and "width" in temp and "height" in temp:
            print('{0}, {1}x{2}'.format(temp["path"], temp["width"], temp["height"]))
            for i in range(0, len(temp["frame"])):
                self.printFrame(temp["frame"][i])
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

    def showHelp(self):
        msg = QMessageBox()
        msg.setWindowTitle("Controls")
        msg.setText(self.helpText)
        msg.move((self.screen.width() - msg.width())/2, (self.screen.height() - msg.height())/2)
        msg.exec_()

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
            self.dimensions = [self.frameGeometry().width(), self.frameGeometry().height()]
        else:
            self.setGeometry(self.screen.x(), self.screen.y(), width, height)
