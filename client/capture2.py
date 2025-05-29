from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time

# Initialize the camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))

# Allow the camera to warm up
time.sleep(2)

print("Press 'q' to quit the video stream")

# Continuously capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array  # Convert the frame to a NumPy array
    
    # Display the frame using OpenCV
    cv2.imshow("Live Video", image)
    
    # Clear the stream for the next frame
    rawCapture.truncate(0)
    
    # Check for the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
