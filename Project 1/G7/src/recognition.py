import cv2
import numpy as np 
import sys
from keyboard import Keyboard
from fingertip import Fingertip
from writer import Writer, Feedback

# CONSTANTS
KNN_MATCH_K = 2
ESC_KEY = 27
BITWISE_AND_CONST = 0xFF
FLANN_INDEX_KDTREE = 1
MIN_MATCH_COUNT = 10

# Shows a camera frame
def showFrame(frame):
    cv2.imshow("Camera", frame)
    return cv2.waitKey(1)

def main():
    # Check if the user specified the keyboard image name
    if sys.argv.__len__() <= 1: 
        print("Error: You need to specify the keyboard name!")
        return

    kb_name = str(sys.argv[1]) # Get name of the Keyboard

    # Create a keyboard by loading it from the JSON file
    keyboard = Keyboard(kb_name)
    
    try:
        keyboard.loadFromJSON()
    except FileExistsError:
        print("Error: File doesn't exist!")
        return -1

    fingertip = Fingertip(keyboard, 8)
    fingertipAux = Fingertip(keyboard, 20)
    writer = Writer()

    kb_img = cv2.imread(keyboard.getImagePath(), 0)

    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(kb_img,None)

    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    image_capture = cv2.VideoCapture(0)

    dst = []

    capslocked = False
    while True:
        _, frame = image_capture.read() #  Read Camera frame

        kp2, des2 = sift.detectAndCompute(frame,None)

        if not hasattr(kp2, '__len__') or len(kp2) <= 0 or KNN_MATCH_K > len(des2): # If the image is black, skip frame
            showFrame(frame)
            continue

        matches = flann.knnMatch(des1,des2,KNN_MATCH_K)

        # Store all the good matches as per Lowe's ratio test.
        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)

        if len(good)>MIN_MATCH_COUNT:
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
            homography, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            h,w,_ = keyboard.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            
            try:
                dst = cv2.perspectiveTransform(pts,homography)
                frame = cv2.polylines(frame,[np.int32(dst)],True,255,3, cv2.LINE_AA)
            except cv2.error:
                pass

            # The Perspective Transform must return an array with 4 points
            if len(dst) == 4:
                found, key = fingertip.analyseFingertipCoordinate(frame, homography)
                _, keyAux = fingertipAux.analyseFingertipCoordinate(frame, homography)

                if found:
                    writer.processKeyAux(frame, keyAux, homography)
                    capslocked = writer.processKey(frame, key, homography)
                else:
                    writer.key = None
            
            if capslocked:
                Feedback.drawCapsLock(frame)
        else:
            print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
 
        # Stops the program when the user presses the ESC key
        if showFrame(frame) & BITWISE_AND_CONST == ESC_KEY:
            break

    image_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()