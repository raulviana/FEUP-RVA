import cv2
import sys
from keyboard import Keyboard, Key, list_keys, KEYBOARD_IMAGES_PATH
import pyautogui
from feedback import Feedback

# Draw corners of a key
def drawCorners(vertices, img, color):
    cv2.circle(img, vertices[0], 2, color, cv2.LINE_AA)
    cv2.circle(img, vertices[1], 2, color, cv2.LINE_AA)
    cv2.circle(img, vertices[2], 2, color, cv2.LINE_AA)
    cv2.circle(img, vertices[3], 2, color, cv2.LINE_AA)

# Get the corners of a key. Assumes the image is in a front view
def getCorners(contourn):
    extLeft = tuple(contourn[contourn[:, :, 0].argmin()][0])
    extRight = tuple(contourn[contourn[:, :, 0].argmax()][0])
    extTop = tuple(contourn[contourn[:, :, 1].argmin()][0])
    extBot = tuple(contourn[contourn[:, :, 1].argmax()][0])
    point1 = (extLeft[0], extTop[1])
    point2 = (extRight[0], extTop[1])
    point3 = (extRight[0], extBot[1])
    point4 = (extLeft[0], extBot[1])
    return [point1, point2, point3, point4]

# Check if the image click is inside a key's corners
def isInsideCorners(point, extLeftTop, extRightBot):
    return point[0] >= extLeftTop[0] and point[0] <= extRightBot[0] and point[1] >= extLeftTop[1] and point[1] <= extRightBot[1]

# Draw the click in a key
def drawClick(clickPoint, img, corners, colorClick, colorCorners):
    for cs in corners:
        if isInsideCorners(clickPoint, cs[0], cs[2]):
            cv2.rectangle(img, cs[0], cs[2], colorCorners, -1, cv2.LINE_AA)
            cv2.circle(img, clickPoint, 2, colorClick, cv2.LINE_AA)
            cv2.circle(img, cs[0], 2, colorCorners, cv2.LINE_AA)
            cv2.circle(img, cs[1], 2, colorCorners, cv2.LINE_AA)
            cv2.circle(img, cs[2], 2, colorCorners, cv2.LINE_AA)
            cv2.circle(img, cs[3], 2, colorCorners, cv2.LINE_AA)
            return [[c[0], c[1]] for c in cs]
    return []

def main():
    # Check if the user specified the keyboard image name
    if sys.argv.__len__() <= 1: 
        print("Error: You need to specify the keyboard image name!")
        return

    img_name = str(sys.argv[1]) # Get name of the Keyboard
    img_path = KEYBOARD_IMAGES_PATH + img_name
    global img
    img = cv2.imread(img_path) # Read the image

    # Check if the image exists
    if not hasattr(img, "__len__"):
        print("Error: Invalid image!")
        return

    # Covert to grey scale
    imgGrey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Edge Detection
    imgCanny = cv2.Canny(imgGrey, 50, 150, None, 3)

    # Contours Detection
    contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img, contours, -1, (255, 0, 0), 3)

    # Get vertices for all contours
    global corners
    corners = []
    for c in contours:
        points = getCorners(c)
        drawCorners(points, img, (0, 0, 255))
        corners.append(points)

    # Get the key coordinates
    global current_key
    keys = []    
    for key in list_keys:
        print("Choose the '" + key + "' key in the image")
        
        # Creates a key and stores it in the current_key variable
        # The other values of the key will be set inside the selectKey callback
        current_key = Key(value=key)
        cv2.imshow("Keyboard - Original", img)

        # Sets the Mouse Callback
        cv2.setMouseCallback("Keyboard - Original", selectKey)

        # Waits for a key pressing
        cv2.waitKey(0)

        keys.append(current_key)

    # Create and store the keyboard
    keyboard = Keyboard(img_name, [value for value in img.shape], keys)
    keyboard.toJSON()

    # Report purposes
    # cv2.imshow("Canny Edge Detector", imgCanny)
    # cv2.waitKey(0)

    cv2.destroyAllWindows()

# Callback to Select Keys
def selectKey(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
        # Get corners for the click point
        points = drawClick((x, y), img, corners, (0, 255, 0), (0, 255, 255))
        
        # Check if the user pressed the correct key
        if len(points) <= 0:
            return

        current_key.corners = points # Set the current key corners
        if event == cv2.EVENT_RBUTTONDOWN:
            current_key.needs_shift = True
        Feedback.playConfirmSound()
        pyautogui.press("enter") # Force a key pressing

if __name__ == "__main__":
    main()