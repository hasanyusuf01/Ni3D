from picamera import PiCamera
import time

camera = PiCamera()
time.sleep(2)
camera.resolution = (1280, 720)
camera.vflip = True
camera.contrast = 10

# Start the video preview
camera.start_preview()

# Record the video and view it continuously
file_name = "/home/pi/Pictures/video_" + str(time.time()) + ".h264"
print("Start recording...")
camera.start_recording(file_name)

# Record for 10 seconds while showing the preview
camera.wait_recording(100)

camera.stop_recording()
camera.stop_preview()
print("Done.")
