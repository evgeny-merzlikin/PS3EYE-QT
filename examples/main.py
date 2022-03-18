from __archive.working_threads import *

class  CustomDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(CustomDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle('Hello')

        QBtn = QDialogButtonBox.OK | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.pslib = PS3Lib()

        layout = QVBoxLayout()
        self.l = QLabel("")
        self.l.setMinimumSize(QSize(640,480))
        self.l.setAutoFillBackground(True)
        self.l.setScaledContents(True)
        self.l.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor('red'))
        self.l.setPalette(pal)
        b = QPushButton("Start thread!")
        c = QPushButton("Stop thread!")
        b.pressed.connect(self.start_thread)
        c.pressed.connect(self.stop_thread)
        layout.addWidget(self.l)
        layout.addWidget(b)
        layout.addWidget(c)

        w= QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.show()

    @pyqtSlot()
    def closeEvent(self, event):
        print("stopping all threads")
        self.stop_thread()
        print("closing all cameras")
        self.pslib.close_all_cams()
        print("uninit of ps3 lib")
        self.pslib.uninit_lib()
        print("app exit now")

    @pyqtSlot()
    def start_thread(self):
        if not self.pslib.load_lib():
            QMessageBox.about(self, "Error!", "Cannot load PS3 library")
            return
        if not self.pslib.init_lib():
            QMessageBox.about(self, "Error!", "Cannot init PS3 library")
            return
        if self.pslib.count_cams() == 0:
            QMessageBox.about(self, "Error!", "No PS3 cameras connected")
            return
        self.cam = self.pslib.open_cam(cam_id=0, frame_w = 640, frame_h = 480, fps = 80)

        if self.cam is None:
            QMessageBox.about(self, "Error!", "Cannot open camera")
            return
        self.cam.signals.new_frame.connect(self.new_frame_captured)
        # self.worker = Worker()
        # self.worker.signals.new_frame.connect(self.new_frame_captured)
        self.threadpool.start(self.cam)

    def new_frame_captured(self, bgr):
        img = QImage(bgr.data, bgr.shape[1], bgr.shape[0], QImage.Format_RGB888).rgbSwapped()
        self.l.setPixmap(QPixmap.fromImage(img))

    @pyqtSlot()
    def stop_thread(self):
        # self.worker.signals.stop.emit()
        if hasattr(self, 'cam'):
            print("stopping camera worker thread")
            self.cam.event_stop.set()
            self.threadpool.waitForDone()
            print("camera worker thread stopped")
            print("closing camera")
            self.pslib.close_cam(self.cam)
            print("camera closed")

    def criticalError(self, message):
        QMessageBox.about(self, "Error!", message)
        # self.close()


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()