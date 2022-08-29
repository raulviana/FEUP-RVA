from playsound import playsound # Install playsound version 1.2.2
import cv2
import numpy as np

SOUNDS_PATH = '../sounds/'

class Feedback:
    # Plays a confirmation sound
    @staticmethod
    def playConfirmSound():
        playsound(SOUNDS_PATH + 'confirm.mp3')

    # Draws a key's contours in the 3D environment
    @staticmethod
    def drawKey3D(img, corners3D):
        img = cv2.polylines(img,[np.int32(corners3D)],True,255,2, cv2.LINE_AA)
    
    # Draws a key's contours in the 2D and 3D environment
    @staticmethod
    def drawKey(img, key, corners3D):
        Feedback.drawKey3D(img, corners3D)
        h = key.corners[3][1] - key.corners[0][1]
        w = key.corners[1][0] - key.corners[0][0]
        if len(key.value)*12 > w:
            w = len(key.value)*30
        img = cv2.rectangle(img, (10, 10), (int(w), int(h)), (255, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(img, key.value, (int((w-len(key.value)*15) / 2), 42), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

    # Draws text to indicate that Caps Lock is active
    @staticmethod
    def drawCapsLock(img):
        cv2.putText(img, "CAPS", (img.shape[1] - 140, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)