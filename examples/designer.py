from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import ps3eye as ps3
import numpy as np
import cv2

class Ui(QMainWindow):
    camera_started = 0
    update_interval = 1000/60

    binary_threshold = 100
    kernel_size = 3

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("Aerodrums_main_window.ui", self)
        self.horizontalLayout.setContentsMargins(11, -1, -1, -1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frame)
        self.timer.setInterval(12)
        self.start_camera_btn.clicked.connect(lambda: self.start_camera(self.start_camera_btn))

        # self.pixmap = QPixmap(640, 480)
        self.scene = QGraphicsScene(self)

        # self.scene.addPixmap(self.pixmap)
        # g = QGraphicsView()
        # g.fitInView()
        self.graphicsView.setScene(self.scene)
        # self.graphicsView.fitInView()


    def start_camera(self, button):
        if self.camera_started:
            self.timer.stop()
            self.camera.stop()
            self.camera_started = 0
            button.setText("Start camera")
            return
        if not ps3.list_cameras():
            QMessageBox.about(self, "Error", "Sorry, no cameras detected.")
            return
        else:
            print("starting camera id=0")
            try:
                self.camera = ps3.Camera(id=0, size=ps3.CameraParameter.RES_640_480, fps=80, mode=ps3.CameraParameter.RGB )
                self.camera.start()
                self.camera.set_parameter( ps3.CameraParameter.HFLIP, 0)
                self.camera.set_parameter( ps3.CameraParameter.AUTO_GAIN, 0)


            except:
                QMessageBox.about(self, "Error", "Sorry, could not start camera.")
                return
            self.camera_started = 1
            self.timer.start()
            button.setText("Stop camera")

    def display_frame(self):
        if not self.camera_started:
            return
        rgb = self.camera.grab_frame()
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY )
        mask = cv2.blur(gray, (self.kernel_size, self.kernel_size))
        _, mask = cv2.threshold(mask, self.binary_threshold, 255, cv2.THRESH_BINARY)
        # kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        # contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]

        self.frame = mask

        height, width = self.frame.shape[:2]
        bytesPerLine = 1 * width

        image = QImage(self.frame.data, width, height, bytesPerLine, QImage.Format_Grayscale8)


        p = QPixmap.fromImage(image).scaled( self.graphicsView.size(), Qt.KeepAspectRatio)

        self.scene.clear()
        self.scene.addPixmap(p)



if __name__ == "__main__":
    ps3.init()
    app = QApplication([])
    window = Ui()
    window.show()
    app.exec_()