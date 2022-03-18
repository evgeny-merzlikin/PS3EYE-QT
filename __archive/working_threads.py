from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import threading
import queue
import time
import traceback, sys

from ctypes import *
import cv2
import sys
import numpy as np

class WorkerSignals(QObject):
    stop = pyqtSignal()
    new_frame = pyqtSignal(object)

class Worker(QRunnable):

    def __init__(self):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()
        self.is_running = True
        self.event_stop = threading.Event()

    @pyqtSlot()
    def run(self):
        print("Thread started")
        counter = 0
        while not self.event_stop.is_set():
            message = "message ID %d" % counter
            print("new frame captured")
            self.signals.new_frame.emit(message)
            time.sleep(3)
            counter += 1

        print("Thread complete")

class PS3Camera(QRunnable):

    def __init__(self, ps3lib, camera_ptr, cam_id, frame_w, frame_h, fps):
        super(PS3Camera, self).__init__()
        self.camera_ptr = camera_ptr
        self.ps3lib = ps3lib
        self.id = cam_id
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.fps = fps

        self.signals = WorkerSignals()
        self.is_running = True
        self.event_stop = threading.Event()

    def disable_hflip(self):
        self.ps3lib.ps3eye_set_parameter(self.camera_ptr, 13, 0)

    @pyqtSlot()
    def run(self):
        # counter = 0
        print("Camera Thread started")
        bayer = np.zeros((self.frame_h, self.frame_w), np.uint8)
        while not self.event_stop.is_set():
            # message = "message ID %d" % counter
            # print("new frame captured")
            self.ps3lib.ps3eye_grab_frame(self.camera_ptr, c_void_p(bayer.ctypes.data))
            bgr = cv2.cvtColor(bayer, cv2.COLOR_BayerGB2BGR)
            self.signals.new_frame.emit(bgr)
            # time.sleep(3)
            # counter += 1

        print("Thread stopped")


class PS3Lib(object):

    def __init__(self):
        self.is_loaded = False
        self.is_inited = False
        self.running_cameras = []

    def load_lib(self):
        if self.is_loaded:
            return True
        if sizeof(c_void_p) == 8:
            file_name = "ps3eye-libusb0x64.dll"
        else:
            file_name = "ps3eye-libusb0.dll"
        try:
            self.ps3lib = CDLL(file_name)
            self.is_loaded = True
        except:
            msg = "ERROR: Unable to load " + file_name
            print(msg)
        finally:
            return self.is_loaded

    def init_lib(self):
        if self.is_inited:
            return True
        if hasattr(self, 'ps3lib'):
            self.ps3lib.ps3eye_init()
            self.is_inited = True
            print("ps3 library dll initialized")
        return self.is_inited

    def uninit_lib(self):
        if self.is_inited:
            self.ps3lib.ps3eye_uninit()
            self.is_inited = False
            print("ps3 library dll un-initialized")

    def count_cams(self):
        if self.is_inited:
            return self.ps3lib.ps3eye_count_connected()
        else:
            return -1

    def open_cam(self, cam_id=0, frame_w = 640, frame_h = 480, fps = 80):
        print("Opening camera id={0}".format(cam_id))
        try:
            camera_ptr = self.ps3lib.ps3eye_open(cam_id, frame_w, frame_h, fps, 0)
            if camera_ptr:
                new_cam = PS3Camera(self.ps3lib, camera_ptr, cam_id, frame_w, frame_h, fps)
                self.running_cameras.append(new_cam)
                print("camera opened id={0} {1}x{2} fps={3}".format(cam_id,frame_w, frame_h, fps) )
                return new_cam
        except:
            print("unable to open camera")
            return None

    def close_all_cams(self):
        for cam in self.running_cameras:
            print("closing camera ID=%d" % cam.cam_id)
            self.ps3lib.ps3eye_close(cam.camera_ptr)
            self.running_cameras.remove(cam)

    def close_cam(self, camera):
        print("closing camera")
        self.ps3lib.ps3eye_close(camera.camera_ptr)
        print("camera closed")
        # self.running_cameras.remove(cam)

