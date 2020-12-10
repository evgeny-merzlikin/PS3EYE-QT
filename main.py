from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("My super app!!")

        label = QLabel("Super cool!")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16,16))
        self.addToolBar(toolbar)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        button_action = QAction(QIcon("webcam.png"), "Start camera", self)
        button_action.setStatusTip("Start camera thread")
        button_action.triggered.connect(self.onMyToolbarButtonClick)
        button_action.setCheckable(True)
        toolbar.addAction(button_action)

        toolbar.addSeparator()

        button_action2 = QAction(QIcon("ui-tab--plus.png"), "Show CV tab", self)
        button_action2.setStatusTip("Show CV tab")
        button_action2.triggered.connect(self.onMyToolbarButtonClick)
        button_action2.setCheckable(True)
        toolbar.addAction(button_action2)

        toolbar.addWidget(QLabel("Hello"))
        toolbar.addWidget(QCheckBox())

        self.setStatusBar(QStatusBar(self))

        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)
        file_menu.addSeparator()
        file_menu.addAction(button_action2)

    def onMyToolbarButtonClick(self, s):
        print("click",s)

    def onWindowTitleChange(self, s):
        print(s)

    def my_custom_fn(self, a="HELLO!", b=5):
        print(a, b)

    def contextMenuEvent(self, event):
        print("Context menu event!")
        super(MainWindow, self).contextMenuEvent(event)


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
