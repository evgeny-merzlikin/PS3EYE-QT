import ps3eye as ps3
import pygame as pg
import numpy as np
import cv2

def cv2ImageToSurface(cv2Image):
    if cv2Image.dtype.name == 'uint16':
        cv2Image = (cv2Image / 256).astype('uint8')
    size = cv2Image.shape[1::-1]
    if len(cv2Image.shape) == 2:
        cv2Image = np.repeat(cv2Image.reshape(size[1], size[0], 1), 3, axis = 2)
        format = 'RGB'
    else:
        format = 'RGBA' if cv2Image.shape[2] == 4 else 'RGB'
        cv2Image[:, :, [0, 2]] = cv2Image[:, :, [2, 0]]
    surface = pg.image.frombuffer(cv2Image.flatten(), size, format)
    return surface.convert_alpha() if format == 'RGBA' else surface.convert()


class VideoCapturePlayer(object):
    size = (320, 240)
    fps = 125

    def __init__(self, **argd):
        self.__dict__.update(**argd)
        super(VideoCapturePlayer, self).__init__(**argd)
        self.display = pg.display.set_mode((800,600), pg.RESIZABLE)
        self.clock = pg.time.Clock()


    def init_cams(self, which_cam_idx):
        print("User selected to start camera %d" % which_cam_idx)
        self.clist = ps3.list_cameras()
        if not self.clist:
            raise ValueError("Sorry, no cameras detected.")
        try:
            cam_id = self.clist[which_cam_idx]
        except IndexError:
            cam_id = self.clist[0]
        self.camera = ps3.Camera(id=which_cam_idx, size=ps3.CameraParameter.RES_320_240, fps=self.fps, mode=ps3.CameraParameter.RGB )
        self.camera.start()
        self.camera.set_parameter( ps3.CameraParameter.HFLIP, 0)
        # self.snapshot = pg.surface.Surface(self.size, 0, self.display)

    def get_and_flip(self):
        if hasattr(self, 'camera'):
            frame = self.camera.grab_frame()
            img = cv2ImageToSurface(frame)
            pg.transform.scale(img, self.display.get_size(), self.display)
            # self.display.blit(img, (0, 0))


    def main(self):
        white = 255, 240, 200
        black = 20, 20, 40
        self.display.fill(black)

        going = True
        # self.init_cams(0)
        # self.init_cams(0)
        while going:
            self.get_and_flip()
            pg.display.update()
            events = pg.event.get()
            for e in events:
                if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                    going = False
                if e.type == pg.KEYDOWN:
                    if e.key in range(pg.K_0, pg.K_0 + 10):
                        if hasattr(self, 'camera'):
                            self.camera.stop()
                        self.init_cams(e.key - pg.K_0)
            self.clock.tick()
        self.camera.stop()

def main():
    pg.init()
    ps3.init()
    VideoCapturePlayer().main()
    # ps3.quit()
    pg.quit()


if __name__ == "__main__":
    main()