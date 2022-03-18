from ctypes import *
import numpy as np
import cv2
import os

_is_init = 0
_ps3lib = None

def init():
    global _is_init, _ps3lib
    if _is_init:
        return
    dir_name = os.path.dirname(__file__)

    if sizeof(c_void_p) == 8:
        file_name = os.path.join("x64","ps3eye-lib.dll")
    else:
        file_name = "ps3eye-lib.dll"
    full_path = os.path.join(dir_name,file_name)

    try:
        _ps3lib = CDLL(full_path)
        _ps3lib.ps3eye_init()
        print("ps3 library inited")
        _is_init = 1
    except:
        raise ValueError("Unable to load %s" % file_name)

def _check_init():
    global _is_init
    if not _is_init:
        raise ValueError("Need to call camera.init() before using.")


def quit():
    global _is_init, _ps3lib
    if _is_init:
        try:
            _ps3lib.ps3eye_uninit()
            print("ps3 library un-inited")
            _is_init = 0
        except:
            raise ValueError("ps3lib.ps3eye_uninit() failed ")

def list_cameras():
    global _ps3lib
    _check_init()
    c = _ps3lib.ps3eye_count_connected()
    # print("detected %d cameras" %c)
    return list(range(c))

class CameraParameter:
    AUTO_GAIN            = 0
    GAIN                 = 1
    AUTO_WHITEBALANCE    = 2
    EXPOSURE             = 3
    SHARPNESS            = 4
    CONTRAST             = 5
    BRIGHTNESS           = 6
    HUE                  = 7
    REDBALANCE           = 8
    BLUEBALANCE          = 9
    GREENBALANCE         = 10
    HFLIP                = 13
    VFLIP                = 12

    BGR                  = 100
    RGB                  = 101
    BAYER                = 102

    RES_640_480          = 103
    RES_320_240          = 104

class Camera:

    def __init__(self, id=0, size=CameraParameter.RES_640_480, fps=60, mode=CameraParameter.RGB):
        """
        Create a new camera instance. ID is camera id starting from 0, size and mode are CameraParameter members.

        :param id:int
        :param size:int
        :param fps:int
        :param mode:int
        """

        _check_init()
        self.id = id
        # self.size = size
        #        w    h
        # size=(640, 480) self.size[1] = 480 = self.h  self.size[0] = 640 = self.w
        # size=(320, 240) self.size[1] = 240 self.size[0] = 320
        # self.size[1] = self.h
        # self.size[0] = self.w


        self.h = 480 if size == CameraParameter.RES_640_480 else 240
        self.w = 640 if size == CameraParameter.RES_640_480 else 320

        self.fps = fps
        self.mode = mode
        self.bayer = np.zeros((self.h, self.w), np.uint8)
        self.frame = np.zeros((self.h, self.w), np.uint8)

    def start(self):
        global _ps3lib
        _check_init()
        try:
            # ps3eye_open(int id, int width, int height, int fps, ps3eye_format outputFormat);
            self.camera_ptr = _ps3lib.ps3eye_open(self.id, self.w, self.h, self.fps, 0)
        except:
            raise ValueError("Could not start camera id=%d" % self.id)
        print("Started camera ID=%d" %self.id)

    def stop(self):
        global _ps3lib
        _check_init()
        try:
            _ps3lib.ps3eye_close(self.camera_ptr)
        except:
            raise ValueError("Could not stop camera id=%d" % self.id)
        print("Stopped camera ID=%d" % self.id)

    def set_parameter(self, par_, val_):
        global _ps3lib
        try:
            _ps3lib.ps3eye_set_parameter(self.camera_ptr, par_, val_)
        except:
            raise ValueError("Could not set parameter %d " % par_ )

    def get_parameter(self, par_):
        global _ps3lib
        try:
            ret = _ps3lib.ps3eye_get_parameter(self.camera_ptr, par_)
        except:
            raise ValueError("Could not get parameter %d" % par_ )
        return ret

    def grab_frame(self):
        global _ps3lib
        if hasattr(self, 'camera_ptr'):
            try:
                _ps3lib.ps3eye_grab_frame(self.camera_ptr, c_void_p(self.bayer.ctypes.data))
            except:
                ValueError("Cannot grab new frame from camera ID=%d" % self.id)
        else:
            ValueError("Cannot grab new frame because camera ID=%d was not started" % self.id)
        if self.mode == CameraParameter.BGR:
            self.frame = cv2.cvtColor(self.bayer, cv2.COLOR_BayerGB2BGR)
        if self.mode == CameraParameter.RGB:
            self.frame = cv2.cvtColor(self.bayer, cv2.COLOR_BayerGB2RGB)
        if self.mode == CameraParameter.BAYER:
            np.copyto(src=self.bayer, where=self.frame)
        return self.frame

