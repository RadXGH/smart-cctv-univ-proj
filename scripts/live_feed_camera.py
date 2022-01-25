from queue import Empty
import cv2
import os

def testCam(src):
    cam = cv2.VideoCapture(src)
    if cam is None or not cam.isOpened():
        return -1
    else:
        return 1

def runCam():
    if testCam(0) == 1:
        cam  = cv2.VideoCapture(0)
        cam.set(3, 800)
        cam.set(4, 450)

        while True:
            ret, img = cam.read()
            cv2.putText(img, 'Press Esc to quit', (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            cv2.imshow('Camera Live Feed', img)

            # press esc to quit
            if cv2.waitKey(1) == 27:
                break

        cv2.destroyAllWindows()
    else:
        print('cam not found')
        return -1

runCam()