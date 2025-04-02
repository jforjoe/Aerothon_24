
![[rotationalsymmetrytriangle.png]]


To rotate the camera view by 90 degrees, we can use OpenCV's `cv2.rotate` function. This function allows us to rotate the frame, and in your case, we need to rotate it clockwise so that the top side of the frame shifts to the right, making objects pass from left to right as the drone moves forward.

Here's the modified code to include this rotation:

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

In this code:
- `cv2.ROTATE_90_CLOCKWISE` rotates the frame 90 degrees clockwise, which aligns with the direction you want.
- Objects will now appear to pass from left to right in the displayed frame as the drone moves forward. 


