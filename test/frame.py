#! /usr/bin/env python2

import sys, random, math, functools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from enum import Enum

SIZE = 10
BRUSH_SIZE = 5
UNDO_SIZE  = 10
KEY_SIZE   = 6

# Key handler to set held keys
class Key():
    def __init__(self):
        self.SHIFT = False
        self.CTRL  = False
        self.ALT   = False
        self.LCLK  = False
        self.MCLK  = False
        self.RCLK  = False

class Frame(QFrame):
    def __init__(self, parent, image):
        super(Frame, self).__init__()
        self.parent = parent
        # Containers
        self.polyIndex = 0
        self.points    = []
        self.frameDict = {}
        self.currPoint = []
        self.image     = image
        # Key variables
        self.keys = Key()
        self.saved    = False
        self.modified = False
        self.toDraw   = True
        # Movement point variables
        self.midClkPos = [0,0]
        self.oldPt = {"x" : -1, "y" : -1}
        self.newPt = self.oldPt
        # Display variables
        self.scaleFactor = 0
        self.invScaleFactor = 0
        self.initUI()

    def initUI(self):
        self.setFocusPolicy(Qt.StrongFocus)
        QToolTip.setFont(QFont('Serif', 10))
        self.setMouseTracking(True)

        self.center()
        self.setWindowTitle('Poly Annotator v0.04')
        pixmap = QPixmap("icon/web.png")
        self.setWindowIcon(QIcon(pixmap))
        self.setGeometry(self.parent.x(), self.parent.y(), self.parent.screen.width(), self.parent.screen.height())
        self.show()

    ### Polygon Functions ###

    # Selects the polygon currently being focused by the frame
    def selectPoly(self, offset):
        if "annotation" in self.frameDict:
            # Firstly we store the current polygon in our dictionary
            if len(self.frameDict["annotation"]) == 0 and len(self.points) > 0:
                self.frameDict["annotation"].append({"p" : self.points})
            elif len(self.points) > 0:
                self.frameDict["annotation"][self.polyIndex]["p"] = list(self.points)

            # Secondly we set the new current polygon
            if len(self.frameDict["annotation"]) > 0:
                self.polyIndex = (self.polyIndex + offset) % len(self.frameDict["annotation"])
                self.points = self.frameDict["annotation"][self.polyIndex]["p"]
            else:
                self.polyIndex = 0
                self.points = []

    # Stores current polygon in the polygon list if it has points, and creates a new polygon
    def addPoly(self):
        if "annotation" not in self.frameDict:
            self.frameDict["annotation"] = []

        if "annotation" in self.frameDict and len(self.points) > 0:
            self.modified = True
            # print(self.polyIndex)
            self.frameDict["annotation"].insert(self.polyIndex, {"p" : list(self.points)})
            # print(self.frameDict["annotation"][self.polyIndex]["p"])
            self.polyIndex += 1
            self.points = []

    # Deletes current polygon in the polygon list
    def delPoly(self):
        self.modified = True
        del self.frameDict["annotation"][self.polyIndex]
        self.selectPoly(-1)

    def sortPolygons(self):
        polygons = []
        if "annotation" in self.frameDict:
            for polygon in self.frameDict["annotation"]:
                # Get centre
                c = [0.0, 0.0]
                for point in polygon["p"]:
                    c = [c[0] + point["x"], c[1] + point["y"]]
                c = [c[0] / float(len(polygon)), c[1] / float(len(polygon))]
                
                # Sort by angle
                # sortedPoly = sorted(polygon["p"], key=functools.cmp_to_key(lambda p1, p2: int(math.atan2(p1["y"] - c[1], p1["x"] - c[0]) - math.atan2(p2["y"] - c[1], p2["x"] - c[0]))))
                
                # Sort by distance in x from centre * distance in y from centre
                sortedPoly = sorted(polygon["p"], key=functools.cmp_to_key(lambda p1, p2: int((p1["x"] - c[0]) * (p2["y"] - c[1]) - (p2["x"] - c[0]) * (p1["y"] - c[1]))))
                polygons.append(sortedPoly)
            # print('sorting! {0}'.format(polygons))
        self.polygons = polygons

    def findNearestPointInPolygon(self, point):
        index = -1
        dist = float('inf')
        for i, pt in enumerate(self.points):
            d = math.sqrt(self.getSquaredDistance([pt["x"], pt["y"]], point))
            if d < dist:
                dist = d
                index = i

        return index

    ### Points Functions ###

    def clearPoints(self):
        self.modified = True
        self.points = []
        if len(self.frameDict["annotation"][self.polyIndex]["p"]) > 0:
            self.delPoly() 

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        # self.move(qr.topLeft())

    def getDistanceToLine(self, p1, p2, p3):
        num = abs((p2[1] - p1[1]) * p3[0] - (p2[0] - p1[0]) * p3[1] + p2[0] * p1[1] - p2[1] * p1[0])
        den = math.sqrt(((p2[1] - p1[1]) ** 2) + ((p2[0] - p1[0]) ** 2))
        return float(num) / float(den)

    def getSquaredDistance(self, p1, p2):
        squaredDistance = 0.0

        if len(p1) != len(p2):
            return float('inf')

        for i in range(0, len(p1)):
            squaredDistance += ((p1[i] - p2[i]) ** 2)

        return squaredDistance

    ### Mouse Functions ###

    def mouseMoveEvent(self, e):
        [x,y] = self.checkBoundary(e.x(), e.y())
        [x,y] = [x * self.invScaleFactor, y * self.invScaleFactor]
        
        self.toDraw = True
        # Translate polygon
        if self.keys.ALT and self.keys.SHIFT and self.keys.LCLK and len(self.points) > 0:
            # Find center of polygon
            c = [0.0, 0.0]

            for point in self.points:
                c = [c[0] + point["x"] * self.scaleFactor, c[1] + point["y"] * self.scaleFactor]

            c = [c[0] / float(len(self.points)), c[1] / float(len(self.points))]

            # Get distance between mouse coordinates and polygon center
            dist = [c[0] - x * self.scaleFactor, c[1] - y * self.scaleFactor]

            # Translate the polygon
            self.points = [{"x" : int(pt["x"] - dist[0]), "y" : int(pt["y"] - dist[1])} for pt in self.points]
            # Check for cleared polygon list
            if self.frameDict != {} and self.polyIndex < len(self.frameDict["annotation"]):
                self.frameDict["annotation"][self.polyIndex]["p"] = self.points
            else:
                self.frameDict["annotation"][0]["p"] = self.points

        # Polygon is a rectangle ... translate an individual point while maintaining the rectangular shape
        elif self.keys.ALT and self.keys.LCLK and len(self.points) == 4:
            [p1, p2, p3, p4] = [self.points[0], self.points[1], self.points[2], self.points[3]]
            x_min = min(p1["x"], min(p2["x"], min(p3["x"], p4["x"])))
            y_min = min(p1["y"], min(p2["y"], min(p3["y"], p4["y"])))
            x_max = max(p1["x"], max(p2["x"], max(p3["x"], p4["x"])))
            y_max = max(p1["y"], max(p2["y"], max(p3["y"], p4["y"])))
            pt = self.points[self.findNearestPointInPolygon([x, y])]
            if pt["x"] == x_min and pt["y"] == y_min:
                x_min = x
                y_min = y
            elif pt["x"] == x_min and pt["y"] == y_max:
                x_min = x
                y_max = y
            elif pt["x"] == x_max and pt["y"] == y_min:
                x_max = x
                y_min = y
            elif pt["x"] == x_max and pt["y"] == y_max:
                x_max = x
                y_max = y

            self.points = [{"x" : x_min, "y" : y_min}, {"x" : x_max, "y" : y_min}, {"x" : x_max, "y" : y_max}, {"x" : x_min, "y" : y_max}]
            self.frameDict["annotation"][self.polyIndex]["p"] = self.points

        elif self.keys.LCLK and self.oldPt != {}:
            temp = next((pt for pt in self.points if pt == self.oldPt), {})
            if temp != {}:
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
            [x,y] = self.checkBoundary(e.x(), e.y())
            [x,y] = [x * self.invScaleFactor, y * self.invScaleFactor]

            self.keys.LCLK = True
            temp = []
            minDist = -1
            ptFound = False
            if len(self.points) > 0:
                minDist = self.getSquaredDistance([self.points[0]["x"] , self.points[0]["y"]], [x, y])
                temp = self.points[0]
            for pt in self.points:
                d = self.getSquaredDistance([pt["x"] , pt["y"]], [x, y])
                if d < (SIZE + SIZE)**2 and d <= minDist:
                    ptFound = True
                    minDist = d
                    temp = pt
            # temp = next((pt for pt in self.points if self.getSquaredDistance([pt["x"] , pt["y"]], [x, y]) < (SIZE + SIZE)**2), [])
            if ptFound:
                # print(temp)
                self.oldPt = temp

        elif e.button() == Qt.MidButton:
            self.keys.MCLK = False

    def mouseReleaseEvent(self, e):
        self.toDraw = True
        if e.button() == Qt.LeftButton:
            [x,y] = self.checkBoundary(e.x(), e.y())
            [x,y] = [x * self.invScaleFactor, y * self.invScaleFactor]

            self.keys.LCLK = False

            # Delete point from polygon
            if self.keys.SHIFT and not self.keys.ALT:
                temp = [z for z in self.points if self.getSquaredDistance([z["x"] , z["y"]], [x, y]) > (SIZE + SIZE)**2]
                if len(self.points) - len(temp) > 0:
                    self.points = [z for z in self.points if self.getSquaredDistance([z["x"] , z["y"]], [x, y]) > (SIZE + SIZE)**2]
                    self.sortPolygons()

            # Add point to polygon
            elif self.keys.CTRL:
                self.points.append({"x" : x, "y" : y})
                self.sortPolygons()

            self.oldPt = []

        elif e.button() == Qt.MidButton:
            self.keys.MCLK = False

    def wheelEvent(self, e):
        self.toDraw = True
        if(e.angleDelta().y() > 0): self.resize(self.width()*0.9, self.height()*0.9)
        elif(e.angleDelta().y() < 0): self.resize(self.width()*1.1, self.height()*1.1)

    def checkBoundary(self, x, y):
        return [max(0, min(x, self.width())), max(0, min(y, self.height()))]

    ### Drawing Functions ###

    def paintEvent(self, e):
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
        # screen = [self.parent.screen.width(), self.parent.screen.height()]
        image  = [self.parent.videoDict["width"], self.parent.videoDict["height"]]

        # aspectRatio = image[0] / image[1]   # Aspect Ratio = image width / image height
        self.scaleFactor = self.parent.dimensions[0] / image[0] # Scale Factor = screen width / screen height 
        if self.scaleFactor != 0:
            self.invScaleFactor = 1 / self.scaleFactor

        # First, draw the image
        if not self.image.isNull():
            qp.drawImage(QPoint(0,(self.parent.frameGeometry().height() - self.parent.dimensions[1]) / 2.0), self.image.scaledToWidth(self.parent.dimensions[0]))

        # Then draw all non-focused polygons
        brush = QBrush(Qt.SolidPattern)
        color = QColor()
        tPoints = []
        if self.frameDict != {} and "annotation" in self.frameDict and len(self.frameDict["annotation"]) > 0:
            count = 0
            for i in range(0, 360, int(360/len(self.frameDict["annotation"]))):
                polygon = self.frameDict["annotation"][count]["p"]
                # sortedPoly = self.sortPoints(polygon)
                qPoints = self.getQPoints(polygon)
                h = i
                s = 90 + random.random()*10
                l = 50 + random.random()*10
                color.setHsl(h, s, l, 127)
                brush.setColor(color)
                qp.setBrush(brush)
                qp.drawConvexPolygon(QPolygon(qPoints))
                count += 1
                if(count >= len(self.frameDict["annotation"])):
                    break
        # Then draw all points
        qp.setPen(QPen(Qt.white, BRUSH_SIZE, Qt.SolidLine))
        size = self.size()
        # sortedPoly = self.sortPoints(self.points)
        qPoints = self.getQPoints(self.points)
        for pt in self.points:  qp.drawEllipse(self.scaleFactor * pt["x"],self.scaleFactor * pt["y"], BRUSH_SIZE, BRUSH_SIZE)

        # Draw outline of focused polygon
        qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        qp.drawConvexPolygon(QPolygon(qPoints))

        # Draw focused polygon
        color.setHsl(255, 255, 255, 127)
        brush.setColor(color)
        qp.setBrush(brush)
        qp.drawConvexPolygon(QPolygon(qPoints))

    def angle(self, pt):
        return math.atan2(self.c['y'] - pt['y'], self.c['x'] - pt['x'])

    def sortPoints(self, points):
        sortedPts = points
        if len(points) > 0:
            self.c = {'x' : 0, 'y' : 0}
            for pt in points:
                [self.c['x'], self.c['y']] = [self.c['x'] + pt['x'], self.c['y'] + pt['y']]
            [self.c['x'], self.c['y']] = [self.c['x'] / len(points), self.c['y'] / len(points)]
            sortedPts = sorted(points, key=self.angle)
        return sortedPts


    # Creates list of QPoints to be turned into a QPolygon
    ## Assumes pList is a list of dictionaries as [{"x" : x0, "y" : y0},  ... , {"x" : xn, "y" : yn}]
    def getQPoints(self, pList):
        qPoints = []
        for i in range(len(pList)):
            if "x" in pList[i]:
                x = pList[i]["x"] + BRUSH_SIZE/2.0
            else:
                x = pList[i][0] + BRUSH_SIZE/2.0
            if "y" in pList[i]:
                y = pList[i]["y"] - BRUSH_SIZE/2.0
            else:
                y = pList[i][1] + BRUSH_SIZE/2.0
            if x < 0 : x = 0
            if y < 0 : y = 0
            if x > self.image.width() : x = self.image.width()
            if y > self.image.height() : y = self.image.height()
            [x, y] = [x * self.scaleFactor, y * self.scaleFactor]
            qPoints += [QPoint(x, y)]
        return qPoints