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

print("Capturing images at 5-second intervals. Press 'q' to quit.")

start_time = time.time()

# Continuously capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array  # Convert the frame to a NumPy array
    
    # Display the frame using OpenCV
    cv2.imshow("Live Video", image)
    
    # Capture an image every 5 seconds
    current_time = time.time()
    if current_time - start_time >= 5:
        # Save the image to a file
        timestamp = int(current_time)
        file_name = f"/home/pi/Pictures/image_{timestamp}.jpg"
        cv2.imwrite(file_name, image)
        print(f"Captured image saved as {file_name}")
        
        # Reset the start time for the next 5-second interval
        start_time = current_time
    
    # Clear the stream for the next frame
    rawCapture.truncate(0)
    
    # Check for the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
