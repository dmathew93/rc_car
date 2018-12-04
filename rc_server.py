from drive_1 import Driver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
import cv2
from time import sleep
from PIL import Image
import io
import base64
import os
from subprocess import Popen, PIPE
driver = Driver()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/test_camera",WebSocket),

    ],debug=True)

class WebSocket(tornado.websocket.WebSocketHandler):
    cap = None
    def check_origin(self, origin):
        return True

    def open(self):
        print("Camera Enabled: ",Popen("sudo modprobe bcm2835-v4l2", shell=True,stdout=PIPE).stdout.read())


        self.converter = Popen([
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', '%dx%d' % (240,240),
            '-r', str(float(30)),
            '-i', '-',
            '-f', 'mpeg1video',
            '-b', '800k',
            '-r', str(float(30)),
            '-'],
            stdin=PIPE, stdout=PIPE, stderr=io.open(os.devnull, 'wb'),
            shell=False, close_fds=True)

        print(self.converter)


        global cap
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            sleep(2)
        self.camera_loop = PeriodicCallback(self.loop,10)
        self.camera_loop.start()
        print("Camera Status ", self.cap.isOpened())

    def loop(self):
        if self.cap.isOpened() is True:
            sio = io.BytesIO()
            ret, frame = self.cap.read()
            img = cv2.flip(frame,-1)
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            img.save(sio, "JPEG")
            try:
                self.write_message(base64.b64encode(sio.getvalue()))
            except tornado.websocket.WebSocketClosedError:
                cap.close()


if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    tornado.ioloop.IOLoop.instance().start()
