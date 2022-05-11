import time
import numpy as np
import cv2
import threading


class camThread(threading.Thread):
    def __init__(self, camName, camID):
        threading.Thread.__init__(self)
        self.camName = camName
        self.camID = camID

    def run(self):
        print ("Starting" + self.camName)
        camPreview(self.camName, self.camID)


def camPreview(camName, camID):
    cv2.namedWindow(camName)
    cam = cv2.VideoCapture(camID)
    if cam.isOpened():  # try to get the first frame
        ret, frame = cam.read()
    else:
        ret = False

    while ret:
        cv2.imshow(camName, frame)
        ret, frame = cam.read()
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break
    cv2.destroyWindow(camName)


# Create two threads as follows
thread1 = camThread("Camera 1", 0)
thread2 = camThread("Camera 2", 1)
thread1.start()
thread2.start()