```python
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.lite.python.interpreter import Interpreter
import os
from datetime import datetime
from picamera2 import Picamera2, Preview

# Function to detect objects in real-time using a TFLite model and Pi Camera
def tflite_detect_pi_camera(model_path, label_path, min_conf=0.5, output_path='output'):
    # Load the label map into memory
    with open(label_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # Load the Tensorflow Lite model into memory
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    float_input = (input_details[0]['dtype'] == np.float32)

    input_mean = 127.5
    input_std = 127.5

    # Initialize Pi Camera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()

    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    while True:
        # Capture an image from the Pi Camera
        frame = picam2.capture_array()
        imH, imW, _ = frame.shape

        # Convert the frame to RGB and resize it to match the model's input shape
        image_resized = cv2.resize(frame, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (non-quantized)
        if float_input:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the frame as input
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[1]['index'])[0]  # Bounding box coordinates
        classes = interpreter.get_tensor(output_details[3]['index'])[0]  # Class index of detected objects
        scores = interpreter.get_tensor(output_details[0]['index'])[0]  # Confidence of detected objects

        # Get the current time for display on the live feed and use it for saving images
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if (scores[i] > min_conf) and (scores[i] <= 1.0):
                # Get bounding box coordinates and draw box
                ymin = int(max(1, (boxes[i][0] * imH)))
                xmin = int(max(1, (boxes[i][1] * imW)))
                ymax = int(min(imH, (boxes[i][2] * imH)))
                xmax = int(min(imW, (boxes[i][3] * imW)))

                # Draw bounding box
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)

                # Draw label
                object_name = labels[int(classes[i])]  # Look up object name from labels array using class index
                label = f'{object_name}: {int(scores[i] * 100)}%'  # Example: 'person: 72%'
                cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Check if the detected object is a "hotspot" and save the frame
                if object_name.lower() == "hotspot":
                    # Add the timestamp to the image (this is displayed on the saved image too)
                    timestamp = f"Time: {current_time}"
                    cv2.putText(frame, timestamp, (10, imH - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    # Format the timestamp for saving
                    timestamp_filename = current_time.replace(":", "-").replace(" ", "_")
                    filename = os.path.join(output_path, f"hotspot_{timestamp_filename}.jpg")
                    cv2.imwrite(filename, frame)
                    print(f"Hotspot detected! Frame saved as {filename}")

        # Display the current time on the live feed
        cv2.putText(frame, f"Time: {current_time}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Show the frame with detection boxes and labels
        cv2.imshow('Object Detection', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources and destroy windows
    picam2.stop()
    cv2.destroyAllWindows()

# Set up paths for the model and label map
MODEL_PATH = 'detect3.tflite'  # Path to the .tflite model file
LABEL_PATH = 'labelmap.txt'  # Path to the labelmap.txt file
MIN_CONFIDENCE = 0.9  # Minimum confidence threshold for displaying detection
OUTPUT_PATH = 'output'  # Directory to save frames with detected hotspots

# Run detection function with Pi Camera
tflite_detect_pi_camera(MODEL_PATH, LABEL_PATH, MIN_CONFIDENCE, OUTPUT_PATH)

```


## Servo_and_object_detection_test

``` python
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.lite.python.interpreter import Interpreter
import os
from datetime import datetime
from picamera2 import Picamera2, Preview
from pymavlink import mavutil

# Initialize Pixhawk connection with timeout for heartbeat
def initialize_pixhawk_connection():
    try:
        pixhawk_connection = mavutil.mavlink_connection('/dev/ttyAMA0', baud=57600, autoreconnect=True)
        pixhawk_connection.wait_heartbeat(timeout=30)
        print("Pixhawk connection established.")
        return pixhawk_connection
    except Exception as e:
        print(f"Error: Could not establish Pixhawk connection - {e}")
        return None

# Function to control the servo using Pixhawk
def control_servo(pixhawk_connection, channel=6, pwm_value=1500):
    if pixhawk_connection:
        pixhawk_connection.mav.command_long_send(
            pixhawk_connection.target_system,
            pixhawk_connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0, channel, pwm_value, 0, 0, 0, 0, 0
        )
        print(f"Servo controlled on channel {channel} with PWM value {pwm_value}.")
    else:
        print("Error: No Pixhawk connection available for servo control.")

# Function to detect objects in real-time using a TFLite model and Pi Camera
def tflite_detect_pi_camera(model_path, label_path, min_conf=0.5, output_path='output'):
    # Load labels
    with open(label_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # Load TFLite model
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    float_input = (input_details[0]['dtype'] == np.float32)
    input_mean, input_std = 127.5, 127.5

    # Initialize Pi Camera
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
        picam2.configure(config)
        picam2.start()
        print("Camera initialized successfully.")
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return

    # Initialize Pixhawk connection
    pixhawk_connection = initialize_pixhawk_connection()
    if pixhawk_connection is None:
        print("Failed to connect to Pixhawk; exiting.")
        return

    # Create output directory
    os.makedirs(output_path, exist_ok=True)

    while True:
        # Capture image from Pi Camera
        frame = picam2.capture_array()
        imH, imW, _ = frame.shape

        # Preprocess frame for model
        image_resized = cv2.resize(frame, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)
        if float_input:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform detection
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[1]['index'])[0]
        classes = interpreter.get_tensor(output_details[3]['index'])[0]
        scores = interpreter.get_tensor(output_details[0]['index'])[0]

        # Display and save detections
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i in range(len(scores)):
            if (scores[i] > min_conf) and (scores[i] <= 1.0):
                ymin = int(max(1, (boxes[i][0] * imH)))
                xmin = int(max(1, (boxes[i][1] * imW)))
                ymax = int(min(imH, (boxes[i][2] * imH)))
                xmax = int(min(imW, (boxes[i][3] * imW)))

                object_name = labels[int(classes[i])]
                label = f'{object_name}: {int(scores[i] * 100)}%'
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
                cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                if object_name.lower() == "target":
                    control_servo(pixhawk_connection)
                    timestamp_filename = current_time.replace(":", "-").replace(" ", "_")
                    filename = os.path.join(output_path, f"target_{timestamp_filename}.jpg")
                    cv2.imwrite(filename, frame)
                    print(f"Target detected! Frame saved as {filename}")

        cv2.putText(frame, f"Time: {current_time}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow('Object Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()

# Run the detection function
tflite_detect_pi_camera('detect3.tflite', 'labelmap.txt', 0.9, 'output')

```