#!/usr/bin/env python

# ---
# An application by Cristi Constantin,
# E-mail : cristi.constantin@live.com,
# Blog : http://cristi-constantin.blogspot.com.
# ---


import os, sys
import math
import time
import json
import binascii
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *


class RotateCorner(QtGui.QGraphicsPixmapItem):
    Type = QtGui.QGraphicsItem.UserType + 3

    def __init__(self, parent, position):
        super(RotateCorner, self).__init__()

        self.init = True
        self.parent = parent
        self.scale = self.parent.scale()

        self.setPos(position)
        self.setZValue(self.parent.zValue())
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)

    def type(self):
        return RotateCorner.Type

    def boundingRect(self):
        if not self.parent.selected:
            return QRectF()
        self.scale = self.parent.scale()
        if self.scale < 0.1:
            self.scale = 0.1
        return QRectF(-8.0*self.scale, -8.0*self.scale, 25.0*self.scale, 25.0*self.scale)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-8.0*self.scale, -8.0*self.scale, 25.0*self.scale, 25.0*self.scale)
        return path

    def paint(self, painter, option, widget):
        if not self.parent.selected:
            self.setActive(False)
            return
        self.setActive(True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)
        painter.drawEllipse(-7*self.scale, -7*self.scale, 18.0*self.scale, 18.0*self.scale)
        painter.setPen(QtGui.QPen(Qt.black, self.scale))
        painter.drawEllipse(-7*self.scale, -7*self.scale, 18.0*self.scale, 18.0*self.scale)

    def mouseReleaseEvent(self, event):
        self.update()
        super(RotateCorner, self).mouseReleaseEvent(event)
        self.setPos(self.new_pos)

    def mouseMoveEvent(self, event):
        #
        # When "init", use scene position.
        if self.init:
            self.init = False
            pos_x = self.parent.scenePos().x()
            pos_y = self.parent.scenePos().y()
        else:
            pos_x = self.x()
            pos_y = self.y()
        #
        # Will return to this position.
        self.new_pos = self.parent.scenePos()
        # Center X and Center Y.
        cntr_x = self.parent.x() + self.parent.pixmap().width()/2
        cntr_y = self.parent.y() + self.parent.pixmap().height()/2
        hypotenuse = math.sqrt( (pos_x-cntr_x) ** 2 + (pos_y-cntr_y) ** 2 )
        radius = self.parent.radius
        # Use parent scale.
        scale = self.parent.scale()
        #
        if pos_x-cntr_x > 0:
            sin_a = (pos_y-cntr_y) / hypotenuse
            rot = math.degrees( math.asin(sin_a) ) + self.parent.norm_angle + 90
            self.parent.real_rot = math.pi - math.asin(sin_a)
        else:
            sin_a = (cntr_y-pos_y) / hypotenuse
            rot = math.degrees( math.asin(sin_a) ) + self.parent.norm_angle + 270
            self.parent.real_rot = 2.0 * math.pi - math.asin(sin_a)
        #
        rot = rot % 360
        self.update()
        if event:
            super(RotateCorner, self).mouseMoveEvent(event)
        # Set parent new rotation.
        self.parent.setRotation(rot)
        # Set left corner position.
        self.parent.lCorner.setPos(
            cntr_x+scale*radius*math.cos(self.parent.real_rot),
            cntr_y-scale*radius*math.sin(self.parent.real_rot)
            )
        #

class ScaleCorner(QtGui.QGraphicsPixmapItem):
    Type = QtGui.QGraphicsItem.UserType + 2

    def __init__(self, parent):
        super(ScaleCorner, self).__init__()

        self.parent = parent
        self.scale = self.parent.scale()
        self.setZValue(self.parent.zValue())
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)

    def type(self):
        return ScaleCorner.Type

    def boundingRect(self):
        if not self.parent.selected:
            return QRectF()
        self.scale = self.parent.scale()
        if self.scale < 0.1:
            self.scale = 0.1
        return QRectF(-8.0*self.scale, -8.0*self.scale, 25.0*self.scale, 25.0*self.scale)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(-8.0*self.scale, -8.0*self.scale, 25.0*self.scale, 25.0*self.scale)
        return path

    def paint(self, painter, option, widget):
        if not self.parent.selected:
            self.setActive(False)
            return
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)
        painter.drawRect(-7*self.scale, -7*self.scale, 18.0*self.scale, 18.0*self.scale)
        painter.setPen(QtGui.QPen(Qt.black, self.scale))
        painter.drawRect(-7*self.scale, -7*self.scale, 18.0*self.scale, 18.0*self.scale)

    def mouseReleaseEvent(self, event):
        self.update()
        super(ScaleCorner, self).mouseReleaseEvent(event)
        self.setPos(self.new_pos_x, self.new_pos_y)

    def mouseMoveEvent(self, event):
        #
        pos_x = self.x()
        pos_y = self.y()
        cntr_x = self.parent.x() + self.parent.pixmap().width()/2
        cntr_y = self.parent.y() + self.parent.pixmap().height()/2
        hypotenuse = math.sqrt( (pos_x-cntr_x) ** 2 + (pos_y-cntr_y) ** 2 )
        radius = self.parent.radius
        # Calculate new scale.
        self.scale = hypotenuse / radius
        #
        self.new_pos_x = cntr_x+self.scale*radius*math.cos(self.parent.real_rot)
        self.new_pos_y = cntr_y-self.scale*radius*math.sin(self.parent.real_rot)
        #
        self.update()
        if event:
            super(ScaleCorner, self).mouseMoveEvent(event)
        # Set parent new scale.
        self.parent.setScale(self.scale)
        # Set left corner position.
        self.parent.rCorner.setPos(self.parent.scenePos())
        #


class Img(QtGui.QGraphicsPixmapItem):
    Type = QtGui.QGraphicsItem.UserType + 1

    def __init__(self, parent, scene, position, rotation, scale, name, pixmap):
        super(Img, self).__init__(pixmap, None, scene)

        self.parent = parent
        self.name = name
        self.selected = False
        self.radius = math.sqrt( (self.pixmap().width()/2.0) ** 2 + (self.pixmap().height()/2.0) ** 2 )
        self.norm_angle = math.degrees( math.asin(self.pixmap().width()/2.0 / self.radius) )

        self.setScale(scale)
        self.setRotation(rotation)
        self.setPos(position)

        self.setTransformOriginPoint(pixmap.width()/2.0, pixmap.height()/2.0)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(1)

        self.rCorner = RotateCorner(self, position)
        self.lCorner = ScaleCorner(self)
        self.rCorner.mouseMoveEvent(None)
        self.lCorner.mouseMoveEvent(None)

    def type(self):
        return Img.Type

    def boundingRect(self):
        pixmap = self.pixmap()
        return QRectF(-10, -10, pixmap.width()+15, pixmap.height()+15)

    def paint(self, painter, option, widget):
        pixmap = self.pixmap()
        painter.drawPixmap(pixmap.rect(), pixmap)
        if self.selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 3, Qt.DotLine))
            painter.drawRoundedRect(-5, -5, pixmap.width()+10, pixmap.height()+10, 5, 5)
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 33), 2, Qt.SolidLine))
            painter.drawRoundedRect(-5, -5, pixmap.width()+10, pixmap.height()+10, 5, 5)

    def mousePressEvent(self, event):
        self.parent.deselectAll()
        self.selected = True
        self.update()
        self.rCorner.update()
        self.lCorner.update()
        super(Img, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        #
        cntr_x = self.x() + self.pixmap().width()/2
        cntr_y = self.y() + self.pixmap().height()/2
        #
        rc = self.radius * self.scale() * math.cos(self.real_rot)
        rs = self.radius * self.scale() * math.sin(self.real_rot)
        #
        self.update()
        super(Img, self).mouseMoveEvent(event)
        self.rCorner.setPos(cntr_x-rc, cntr_y+rs)
        self.lCorner.setPos(cntr_x+rc, cntr_y-rs)
        #



class GraphWidget(QtGui.QGraphicsView):
    def __init__(self):
        super(GraphWidget, self).__init__()

        self.setWindowTitle('Gnome Presentation')
        self.setMinimumSize(600, 600)

        scene = QtGui.QGraphicsScene(self)
        scene.setSceneRect(0, 0, 5000, 5000)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtGui.QGraphicsView.SmartViewportUpdate)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setScene(scene)

        # Load presentation file. It's a plain JSON file.
        items_json = json.load(open('prez1.prez'))
        # Save all item pointers in a dictionary.
        self.items_dict = {}
        # List used for circling items when pressing Space or Return.
        self.circ_items = []
        # First item is currently None.
        self.currentItem = None
        # Trajectory bewteen current item and next item.
        self.trajectoryLine = QLineF()
        # TimeLine for smooth moving to next item.
        self.smoothMoveTimer = QTimeLine(2000, self)
        self.smoothMoveTimer.setFrameRange(0, 1)
        self.smoothMoveTimer.setEasingCurve(QEasingCurve.OutQuart)
        self.smoothMoveTimer.valueChanged.connect(self.smoothMove)

        for k in items_json:
            #
            d = items_json[k]
            if d['path'] and os.path.exists(d['path']):
                pixmap = QtGui.QPixmap(d['path'])
            else:
                pixmap = QtGui.QPixmap()
                if d['data']:
                    pixmap.loadFromData(binascii.a2b_base64(d['data']))
            #
            itm = Img(self, scene, QPointF(d['pos'][0], d['pos'][1]), d['rotation'], d['scale'], k, pixmap)
            self.items_dict[k] = itm
            scene.addItem(itm.rCorner)
            scene.addItem(itm.lCorner)
            #

    def smoothMove(self, value):
        #
        pos = self.trajectoryLine.pointAt(value)
        rect = QRectF(pos, self.currentItem.boundingRect().size())
        self.fitInView(rect, Qt.KeepAspectRatio)
        #
        if value == 1.0:
            self.update()
            self.smoothMoveTimer.stop()
        #

    def keyPressEvent(self, event):
        #
        key = event.key()

        if key == Qt.Key_Plus:
            self.scaleView(1.2)

        elif key == Qt.Key_Minus:
            self.scaleView(1 / 1.2)

        elif key == Qt.Key_Space or key == Qt.Key_Enter:
            #
            if self.smoothMoveTimer.state() == QTimeLine.Running:
                return
            #
            if not self.circ_items:
                self.circ_items = [self.items_dict[k] for k in sorted(self.items_dict.keys(),reverse=True)]
            # Pop one item from items list.
            item = self.circ_items.pop()
            if not self.currentItem:
                self.currentItem = item
                self.centerOn(item)
                self.fitInView(item, Qt.KeepAspectRatio)
            else:
                self.trajectoryLine = QLineF(self.currentItem.scenePos(), item.scenePos())
                self.currentItem = item
                self.smoothMoveTimer.start()
            #

        else:
            super(GraphWidget, self).keyPressEvent(event)
        #

    def wheelEvent(self, event):
        self.scaleView(math.pow(1.25, event.delta() / 240.0))

    def drawBackground(self, painter, rect):
        #
        sceneRect = self.sceneRect()
        # Fill.
        gradient = QtGui.QLinearGradient(sceneRect.topLeft(), sceneRect.bottomRight())
        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(1, Qt.lightGray)
        painter.fillRect(rect.intersect(sceneRect), QtGui.QBrush(gradient))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(sceneRect)
        #

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.03 or factor > 40:
            return
        self.scale(scaleFactor, scaleFactor)

    def deselectAll(self):
        for itm in self.items_dict.values():
            itm.selected = False
            itm.update()
            itm.rCorner.update()
            itm.lCorner.update()

    def mouseDoubleClickEvent(self, event):
        self.deselectAll()
        super(GraphWidget, self).mouseDoubleClickEvent(event)



if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    widget = GraphWidget()
    widget.show()
    sys.exit(app.exec_())

# Eof()
