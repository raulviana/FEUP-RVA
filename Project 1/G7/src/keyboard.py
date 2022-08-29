import json

# Constants
JSON_FILE_PATH = "../files/"
KEYBOARD_IMAGES_PATH = "../keyboards/"

class Keyboard:
    # Class constructor: Needs the Image Name
    def __init__(self, image_name, shape = [], keys = []):
        self._image_name = image_name
        self._shape = shape
        self._keys = keys

    # Keyboard Shape Property (Height, Length, Channels)
    # Gets the shape property
    @property
    def shape(self):
        return self._shape

    # Sets the shape property
    @shape.setter
    def shape(self, v):
        self._shape = [int(_v) for _v in v]

    # Keyboard Keys Property. It should be an array of Key objects
    # Gets the keys property
    @property
    def keys(self):
        return self._keys

    # Sets the keys property
    @keys.setter
    def keys(self, v):
        self._keys = v

    # Keyboard Image Name Property. It should be a string
    # Gets the image_name property
    @property
    def image_name(self):
        return self._image_name

    # Sets the image_name property
    @image_name.setter
    def image_name(self, v):
        self._image_name = v

    # OTHER CLASS METHODS
    
    # Gets the keyboard image size (length, height)
    def getSize(self):
        return (self.shape[1], self.shape[0])

    # Gets the keyboard image path
    def getImagePath(self):
        return KEYBOARD_IMAGES_PATH + self.image_name

    # Converts the Keyboard class into the JSON format, and store it in a file
    def toJSON(self):
        json_path = JSON_FILE_PATH + self.image_name + ".json"
        try:
            f = open(json_path, "x") # Tries to create the file
        except FileExistsError:
            f = open(json_path, "w") # If the file already exists, it overwrites the current file
        f.write(json.dumps({ "shape": [str(shape) for shape in self.shape], "keys": [key.toJSON() for key in self.keys] }))
        f.close()

    # Loads the Keyboard class from a JSON file
    def loadFromJSON(self):
        f = open(JSON_FILE_PATH + self.image_name + ".json") # Opens the file
        dict = json.load(f)
        keys = [Key(key['value'], key['needs_shift'], key['corners']) for key in dict['keys']]
        self.shape = dict['shape']
        self.keys = keys

class Key:
    # Class Constructor: Needs the Key value
    def __init__(self, value, needs_shift = False, corners = []):
        self._value = value
        self._needs_shift = needs_shift
        self._corners = [list(map(float, sublist)) for sublist in corners]

    # Key Value Property. It should be a char value
    # Gets the value property
    @property
    def value(self):
        return self._value
    
    # Sets the value property
    @value.setter
    def value(self, v):
        self._value = v

    # Key Corners Property. It should be an array of pairs of floats, with the key corners coordinates
    # Gets the corners property
    @property
    def corners(self):
        return self._corners

    # Sets the corners property
    @corners.setter
    def corners(self, v):
        self._corners = v

    # Key Needs Shift Property. It should be a boolean
    # Gets the needs_shift property
    @property
    def needs_shift(self):
        return self._needs_shift

    # Sets the needs_shift property
    @needs_shift.setter
    def needs_shift(self, v):
        self._needs_shift = v

    # OTHER CLASS METHODS

    # Convert the Key class into the JSON format
    def toJSON(self):
        return {"value": self.value, "needs_shift": self.needs_shift, "corners": [[str(corner[0]), str(corner[1])] for corner in self.corners]}

    # Operator ==
    def __eq__(self, other):
        return isinstance(other, Key) and self.value == other.value

# List of Keys accepted by our program
list_keys = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "ENTER", "SPACE", "BACKSPACE", "CAPSLOCK", "SHIFT", ",", ".", "|", ">"]