#! /usr/bin/env python2

import sys, random, math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from enum import Enum

SIZE = 10
BRUSH_SIZE = 5
UNDO_SIZE  = 10
KEY_SIZE   = 6

class Key():
    def __init__(self):
        self.SHIFT = False
        self.CTRL  = False
        self.ALT   = False
        self.LCLK  = False
        self.MCLK  = False
        self.RCLK  = False

##### GENERIC FRAME CLASS #####
class Frame(QFrame):
    def __init__(self, parent, image):
        super(Frame, self).__init__()
        self.parent = parent
        # Containers
        self.polyIndex = 0
        self.points = []
        self.frameDict = {}
        self.currPoint = []
        self.image = image
        # Key variables
        self.keys = Key()
        self.saved = False
        self.modified = False
        self.toDraw = True
        # Movement point variables
        self.midClkPos = [0,0]
        self.oldPt = []
        self.newPt = []
        self.initUI()

    def initUI(self):
        self.setFocusPolicy(Qt.StrongFocus)
        QToolTip.setFont(QFont('Serif', 10))
        self.setMouseTracking(True)

        self.center()
        self.setWindowTitle('Poly Annotator v0.03')
        pixmap = QPixmap("icon/web.png")
        self.setWindowIcon(QIcon(pixmap))
        self.setGeometry(self.parent.x(), self.parent.y(), self.image.width(), self.image.height())
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
        if len(self.frameDict["annotation"]) == 0 and len(self.points) > 0:
            self.frameDict["annotation"].append({"p" : self.points})
        elif len(self.points) > 0:
            self.frameDict["annotation"][self.polyIndex] = {"p" : list(self.points)}

        if len(self.frameDict["annotation"]) > 0:
            self.polyIndex = (self.polyIndex + offset) % len(self.frameDict["annotation"])
            self.points = self.frameDict["annotation"][self.polyIndex]
        else:
            self.polyIndex = 0
            self.points = []

    def addPoly(self):
        if len(self.points) > 0:
            self.modified = True
            self.frameDict["annotation"][self.polyIndex] = {"p" : list(self.points)}
            self.polyIndex += 1
            self.points = []

    def delPoly(self):
        self.modified = True
        del self.frameDict["annotation"][self.polyIndex]
        self.selectPoly(-1)

    def clearPoints(self):
        self.modified = True
        self.points = []
        if len(self.frameDict["annotation"][self.polyIndex]["p"]) > 0:
            self.delPoly()

    ### Drawing Functions ###
    def paintEvent(self, e):
        # if self.toDraw == True or self.modified == True:
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()
        self.setWindowTitle('Poly Annotator v0.03')
        pixmap = QPixmap("icon/web.png")
        self.setWindowIcon(QIcon(pixmap))
        self.update()
        self.setMouseTracking(True)
        self.toDraw = False

    def draw(self, qp):
        # First, draw the image
        qp.drawImage(QPoint(0,0), self.image)
        # Then draw all other polygons
        brush = QBrush(Qt.SolidPattern)
        color = QColor()
        tPoints = []
        if self.frameDict != {} and "annotation" in self.frameDict and len(self.frameDict["annotation"]) > 0:
            count = 0

            for i in range(0, 360, int(360/len(self.frameDict["annotation"]))):
                polygon = self.frameDict["annotation"][count]["p"]
                for k in range(0, len(polygon)):
                    if("x" in polygon[k] and "y" in polygon[k]):
                        tPoints.append([polygon[k]["x"], polygon[k]["y"]])
                qPoints = self.getQPoints(tPoints) # May need changing
                h = i
                s = 90 + random.random()*10
                l = 50 + random.random()*10
                color.setHsl(h, s, l, 127)
                brush.setColor(color)
                qp.setBrush(brush)
                qp.drawPolygon(QPolygon(qPoints))
                count += 1
                if(count >= len(self.frameDict["annotation"])):
                    break
        # Then draw all points
        qp.setPen(QPen(Qt.white, BRUSH_SIZE, Qt.SolidLine))
        size = self.size()
        qPoints = self.getQPoints(tPoints)
        for pt in tPoints:
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

    def getDistanceToLine(self, p1, p2, p3):
        num = abs((p2[1] - p1[1]) * p3[0] - (p2[0] - p1[0]) * p3[1] + p2[0] * p1[1] - p2[1] * p1[0])
        den = math.sqrt(((p2[1] - p1[1]) ** 2) + ((p2[0] - p1[0]) ** 2))
        return float(num) / float(den)

    def mouseMoveEvent(self, e):
        [x,y] = self.checkBoundary(e.x(),e.y())
        self.toDraw = True
        # Translate polygon
        if self.keys.ALT and self.keys.SHIFT and self.keys.LCLK and len(self.points) > 0:
            # Find center of polygon
            c = [0.0, 0.0]

            for point in self.points:
                c = [c[0] + point[0], c[1] + point[1]]

            c = [c[0] / float(len(self.points)), c[1] / float(len(self.points))]

            # Get distance between mouse coordinates and polygon center
            dist = [c[0] - x, c[1] - y]

            # Translate the polygon
            self.points = [[int(pt[0] - dist[0]), int(pt[1] - dist[1])] for pt in self.points]
            # Check for cleared polygon list
            if self.frameDict != {} and self.polyIndex < len(self.frameDict["annotation"]):
                self.frameDict["annotation"][self.polyIndex]["p"] = self.points
            else:
                self.frameDict["annotation"][0]["p"] = self.points

        # Polygon is a rectangle ... translate an individual point while maintaining the rectangular shape
        elif self.keys.ALT and self.keys.LCLK and len(self.points) == 4:
            p1 = self.points[0]
            p2 = self.points[1]
            p3 = self.points[2]
            p4 = self.points[3]
            x_min = min(p1[0], min(p2[0], min(p3[0], p4[0])))
            y_min = min(p1[1], min(p2[1], min(p3[1], p4[1])))
            x_max = max(p1[0], max(p2[0], max(p3[0], p4[0])))
            y_max = max(p1[1], max(p2[1], max(p3[1], p4[1])))
            pt = self.points[self.findNearestPointInPolygon([x, y])]

            if pt[0] == x_min and pt[1] == y_min:
                x_min = x
                y_min = y
            elif pt[0] == x_min and pt[1] == y_max:
                x_min = x
                y_max = y
            elif pt[0] == x_max and pt[1] == y_min:
                x_max = x
                y_min = y
            elif pt[0] == x_max and pt[1] == y_max:
                x_max = x
                y_max = y

            self.points = [[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]]
            self.frameDict["annotation"][self.polyIndex]["p"] = self.points

        elif self.keys.LCLK and self.oldPt != []:
            temp = next((pt for pt in self.points if pt == self.oldPt), [])
            if temp != []:
                index = self.points.index(self.oldPt)
                self.points.remove(temp)
                self.points.insert(index, {"x" : x, "y" : y})
                self.oldPt = {"x" : x, "y" : y}
            # self.newPt = [x, y]

        elif self.keys.MCLK:
            offset = [x - self.midClkPos[0], y - self.midClkPos[1]]
            self.move(self.x() + offset[0], self.y() + offset[1])

    def mousePressEvent(self, e):
        self.toDraw = True
        if e.button() == Qt.LeftButton:
            [x,y] = self.checkBoundary(e.x(),e.y())

            self.keys.LCLK = True
            temp = next((pt for pt in self.points if self.getSquaredDistance(pt, [x, y]) < (SIZE + SIZE)**2), [])
            if temp != []:
                # print(temp)
                self.oldPt = temp

        elif e.button() == Qt.MidButton:
            self.keys.MCLK = False

    def mouseReleaseEvent(self, e):
        self.toDraw = True
        if e.button() == Qt.LeftButton:
            [x,y] = self.checkBoundary(e.x(),e.y())

            self.keys.LCLK = False

            # Delete point from polygon
            if self.keys.SHIFT and not self.keys.ALT:
                temp = [z for z in self.points if self.getSquaredDistance(z, [x, y]) > (SIZE + SIZE)**2]
                if len(self.points) - len(temp) > 0:
                    self.points = [z for z in self.points if self.getSquaredDistance(z, [x, y]) > (SIZE + SIZE)**2]
                    self.sortPolygons()

            # Add point to polygon
            elif self.keys.CTRL:
                self.points.append({"x" : x, "y" : y})
                self.sortPolygons()

            self.oldPt = []

        elif e.button() == Qt.MidButton:
            self.keys.MCLK = False

    def sortPolygons(self):
        polygons = []

        for polygon in self.frameDict["annotation"]:
            c = [0.0, 0.0]

            for point in polygon["p"]:
                c = [c[0] + point["x"], c[1] + point["y"]]

            c = [c[0] / float(len(polygon)), c[1] / float(len(polygon))]
            polygons.append(sorted(polygon, cmp=lambda p1, p2: int((p1[0] - c[0]) * (p2[1] - c[1]) - (p2[0] - c[0]) * (p1[1] - c[1]))))

        self.polygons = polygons

    def findNearestPointInPolygon(self, point):
        index = -1
        dist = float('inf')
        for i, pt in enumerate(self.points):
            d = math.sqrt(self.getSquaredDistance(pt, point))
            if d < dist:
                dist = d
                index = i

        return index

    def getSquaredDistance(self, p1, p2):
        squaredDistance = 0.0

        if len(p1) != len(p2):
            return float('inf')

        for i in range(0, len(p1)):
            squaredDistance += ((p1[i] - p2[i]) ** 2)

        return squaredDistance

    def wheelEvent(self, e):
        self.toDraw = True
        if(e.angleDelta().y() > 0):
            self.resize(self.width()*0.9, self.height()*0.9)
        elif(e.angleDelta().y() < 0):
            self.resize(self.width()*1.1, self.height()*1.1)

    def checkBoundary(self, x, y):
        return [max(0, min(x, self.width())), max(0, min(y, self.height()))]
