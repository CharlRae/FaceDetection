# Libraries
import cv2

# Class sub programs
class CameraDevice:

    def __init__(self, camera_port) -> None:
       # Initializes the CameraDevice object
       # Sets the opencv video capture device to be the camera of specified port
       self.cam = cv2.VideoCapture(camera_port)

    def read_frame(self):
        # Returns a single frame from the camera as a 2D list
        _, frame = self.cam.read()
        return frame
    
    def grayscale_image(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray_image
    
    def recolour_image(self, image):
        bgr_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        return bgr_image
    
    
    def resize_image(self, image, size):
        resized_image = cv2.resize(image, size)
        return resized_image

    def show_image(self, image):
        # Displays a frame on the screen
        cv2.imshow('frame', image)
