import ps3eye as ps3
import numpy as np
import cv2

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(800, 600)
        canvas.fill(QtGui.QColor("white"))
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

    def paintEvent(self, event):

        from random import randint
        painter = QtGui.QPainter(self.label.pixmap())

        frame = camera.grab_frame()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA )

        height, width = gray.shape[:2]
        bytesPerLine = 1 * width
        img = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGBA8888).scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio )

        painter.drawImage(QtCore.QPoint(0, 0), img)

        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor('green'))
        painter.setPen(pen)

        font = QtGui.QFont()
        font.setFamily('Times')
        font.setBold(True)
        font.setPointSize(40)
        painter.setFont(font)
        painter.drawText(QtCore.QPoint(100, 100), 'PS3EYE')
        painter.drawEllipse(QtCore.QPoint(100, 100), 10, 10)
        painter.drawEllipse(QtCore.QPoint(100, 100), 15, 20)
        painter.drawEllipse(QtCore.QPoint(100, 100), 20, 30)
        painter.drawEllipse(QtCore.QPoint(100, 100), 25, 40)
        painter.drawEllipse(QtCore.QPoint(100, 100), 30, 50)
        painter.drawEllipse(QtCore.QPoint(100, 100), 35, 60)

        painter.end()
        self.update()

ps3.init()
if ps3.list_cameras():
    camera = ps3.Camera()
    camera.start()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec_()

if camera:
    camera.stop()
ps3.quit()