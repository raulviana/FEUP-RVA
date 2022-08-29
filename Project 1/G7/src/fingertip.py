import numpy as np
import mediapipe as mp
import cv2

class Fingertip:
    # Class Constructor: Needs an Object of the type keyboard
    def __init__(self, keyboard, id):
        self._keyboard = keyboard
        mpHands = mp.solutions.hands
        self._hands = mpHands.Hands(static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5)
        self._position = (0.0, 0.0)
        self._current_key = None
        self._finger_id = id

    # Property Hands Getter
    @property
    def hands(self):
        return self._hands

    # Property Keyboard Getter
    @property
    def keyboard(self):
        return self._keyboard

    # Property Position Getter
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, v):
        self._position = v

    # Property Current Key
    @property
    def current_key(self):
        return self._current_key

    @current_key.setter
    def current_key(self, v):
        self._current_key = v

    # Property Finger Id
    @property
    def finger_id(self):
        return self._finger_id
    
    @finger_id.setter
    def finger_id(self, v):
        self._finger_id = v

    # Analyse fingertip's coordinate
    def analyseFingertipCoordinate(self, frame, homography):
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frameRGB)
        height, width, _ = frameRGB.shape
        
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    if id == self.finger_id: 
                        if Fingertip.isInsideImage(lm.x, width, lm.y, height) and (not homography is None) and homography.ndim >= 2:
                            homography_inverse = np.linalg.inv(homography)
                            ft = (int(lm.x * width), int(lm.y * height))
                            self.position = cv2.perspectiveTransform(np.float32(ft).reshape(-1,1,2), homography_inverse)[0][0]
                            cv2.circle(frame, ft, 2, (0,255,0), cv2.LINE_AA)
        else: self._position = (0.0, 0.0)

        #is finger over a key?
        return self.isFingerOverKey()

    # Check if the fingertip is inside a key
    def isFingertipInsideKey(self, corners): # Assuming the keys are squares
        if(len(corners) != 0):
            return corners[0][0] <= self.position[0] <= corners[1][0] and corners[0][1] <= self.position[1] <= corners[3][1]
        else:
            return False


    # Check if the finger is over a key
    def isFingerOverKey(self):
        if self.current_key != None:
            if (not self.current_key is None) and self.isFingertipInsideKey(self.current_key.corners): # Still inside the same key 
                return True, self.current_key

        found = False

        # Check if fingertip is inside other keys
        for key in self.keyboard.keys:
            corners = key.corners

            if self.isFingertipInsideKey(corners):
                found = True
                self.current_key = key
                break

        # Resetting key if not found
        if not found:
            self.current_key = None

        return found, self.current_key

    @staticmethod
    def isInsideImage(x,  width, y, height,):
        x_position = x * width
        y_position = y * height
        return (x_position > 0 and x_position < width) and (y_position > 0 and y_position < height)