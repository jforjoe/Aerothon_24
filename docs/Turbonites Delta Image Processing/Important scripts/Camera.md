## Camera Test

```python
import cv2
from picamera2 import Picamera2

# Initialize the camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 30
picam2.configure("preview")

# Start the camera
picam2.start()

# Stream video until 'q' is pressed
try:
    while True:
        # Capture the image from the camera
        frame = picam2.capture_array()

        # Display the frame using OpenCV
        cv2.imshow("Raspberry Pi Camera", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Streaming stopped manually.")

finally:
    # Stop the camera and close windows
    picam2.stop()
    cv2.destroyAllWindows()
    print("Video stream ended.")
```



## Camera Resolution 

```python
import cv2
from picamera2 import Picamera2

# Initialize the camera
picam2 = Picamera2()

# Set to capture at a high resolution for full FOV, e.g., 1920x1080
picam2.preview_configuration.main.size = (1920, 1080)  # Maximize FOV resolution
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 30
picam2.configure("preview")

# Start the camera
picam2.start()

# Desired lower resolution while keeping the full FOV
target_resolution = (1080, 810)

# Stream video until 'q' is pressed
try:
    while True:
        # Capture the high-res image from the camera
        frame = picam2.capture_array()

        # Downscale to the desired resolution
        frame_resized = cv2.resize(frame, target_resolution, interpolation=cv2.INTER_LINEAR)

        # Display the downscaled frame using OpenCV
        cv2.imshow("Raspberry Pi Camera with Full FOV at Lower Resolution", frame_resized)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Streaming stopped manually.")

finally:
    # Stop the camera and close windows
    picam2.stop()
    cv2.destroyAllWindows()
    print("Video stream ended.")

```


## Image Rotation

```python
import cv2
from picamera2 import Picamera2

# Initialize the camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 30
picam2.configure("preview")

# Start the camera
picam2.start()

# Stream video until 'q' is pressed
try:
    while True:
        # Capture the image from the camera
        frame = picam2.capture_array()

        # Rotate the frame 90 degrees clockwise
        frame_rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Display the rotated frame using OpenCV
        cv2.imshow("Raspberry Pi Camera", frame_rotated)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Streaming stopped manually.")

finally:
    # Stop the camera and close windows
    picam2.stop()
    cv2.destroyAllWindows()
    print("Video stream ended.")

```



## Video recording

```python
import cv2
from picamera2 import Picamera2
import time

# Initialize the camera
picam2 = Picamera2()

# Set to capture at a high resolution for full FOV, e.g., 1920x1080
picam2.preview_configuration.main.size = (640, 480)  # Maximize FOV resolution
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 30
picam2.configure("preview")

# Start the camera
picam2.start()

# Define the codec and create VideoWriter object for saving video in MP4 format
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 file
out = cv2.VideoWriter('recorded_video.mp4', fourcc, 30.0, (1920, 1080))  # Save at 1920x1080 resolution

print("Recording video... Press 'q' to stop.")

try:
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()

        # Write the frame to the video file (without rotation)
        out.write(frame)

        # Show the frame in a window (optional, for monitoring)
        cv2.imshow("Recording", frame)

        # Stop recording if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Recording stopped by user.")
            break

except KeyboardInterrupt:
    print("Recording stopped manually.")

finally:
    # Release everything when the job is finished
    picam2.stop()
    out.release()
    cv2.destroyAllWindows()
    print("Video saved as 'recorded_video.mp4'")

```


