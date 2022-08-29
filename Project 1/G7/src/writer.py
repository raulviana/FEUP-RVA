import time
import numpy as np
import cv2

from feedback import Feedback

TIME_PROCESS_KEY = 0.5 # 1 second input to process key

class Writer:
    def __init__(self):
        self._key = None
        self._time_processing = time.time()
        self._text = ""
        self._capslocked = False
        self._shiftlocked = False

    # Key Property
    @property
    def key(self):
        return self._key
    
    @key.setter
    def key(self, v):
        self._key = v

    # Time Processing Property
    @property
    def time_processing(self):
        return self._time_processing
    
    @time_processing.setter
    def time_processing(self, v):
        self._time_processing = v

    # Text Property
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, v):
        self._text = v

    # Capslocked Property
    @property
    def capslocked(self):
        return self._capslocked
    
    @capslocked.setter
    def capslocked(self, v):
        self._capslocked = v

    # shiftlocked Property
    @property
    def shiftlocked(self):
        return self._shiftlocked
    
    @shiftlocked.setter
    def shiftlocked(self, v):
        self._shiftlocked = v

    # Get char to write for keys
    def getText(self, key):
        if key.value == 'CAPSLOCK':
            self.capslocked = not self.capslocked
            return self.text + ""
        values = {
            'SPACE': self.text + ' ',
            'ENTER': self.text + '\n',
            'BACKSPACE': self.text[:-1]
        }
        if (((not self.capslocked) and (not self.shiftlocked)) or (self.capslocked and self.shiftlocked)) and len(key.value) == 1 and key.value.isalpha():
            return values.get(key.value, self.text + chr(ord(key.value) + 32))
        return values.get(key.value, self.text + key.value)

    # Process key detection
    def processKey(self, frame, key, homography):
        if (self.key != key):
            self.key = key
            self._time_processing = time.time()
        if time.time() - self.time_processing > TIME_PROCESS_KEY and ((key.needs_shift and self.shiftlocked) or not key.needs_shift):
            self.text = self.getText(key)
            self.time_processing = time.time()
            Feedback.playConfirmSound()
            print(self.text)
            self.key = None

        try:
            pts = np.float32([ key.corners[0],key.corners[1],key.corners[2],key.corners[3] ]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts,homography)
            Feedback.drawKey(frame, key, dst)
        except cv2.error:
            pass

        return self.capslocked
    
    # Process key detection
    def processKeyAux(self, frame, keyAux, homography):
        if keyAux and keyAux.value == "SHIFT":
            ptsShift = np.float32([ keyAux.corners[0],keyAux.corners[1],keyAux.corners[2],keyAux.corners[3] ]).reshape(-1,1,2)
            dstShift = cv2.perspectiveTransform(ptsShift,homography)
            Feedback.drawKey3D(frame, dstShift)
            self.shiftlocked = True
        else: self.shiftlocked = False
        