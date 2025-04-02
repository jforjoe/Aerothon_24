```python

#final
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.lite.python.interpreter import Interpreter
from datetime import datetime
from picamera2 import Picamera2
import os

# Function to detect squares, triangles, and circles in real-time using a TFLite model and PiCamera2
def tflite_detect_picamera(model_path, label_path, output_dir, circle_output_dir, min_conf=0.9):
    # Load the label map into memory
    with open(label_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # Load the TensorFlow Lite model into memory
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

    # Initialize PiCamera2
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
    picam2.start()

    # Create directories if they don't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(circle_output_dir):
        os.makedirs(circle_output_dir)

    while True:
        # Capture frame from the camera in RGB format
        frame = picam2.capture_array()

        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize the frame to match the model's input shape
        imH, imW, _ = frame.shape
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

        square_count = 0
        triangle_count = 0
        circle_detected = False

        # Loop over all detections and process square, triangle, and circle
        for i in range(len(scores)):
            if (scores[i] > min_conf) and (scores[i] <= 1.0):
                object_name = labels[int(classes[i])]  # Look up object name from labels array using class index

                # Count squares and triangles only
                if object_name == "square":
                    square_count += 1
                elif object_name == "triangle":
                    triangle_count += 1
                elif object_name == "circle":
                    circle_detected = True  # Mark that a circle is detected

                # Get bounding box coordinates and draw box for squares, triangles, and circles
                if object_name in ["square", "triangle", "circle"]:
                    ymin = int(max(1, (boxes[i][0] * imH)))
                    xmin = int(max(1, (boxes[i][1] * imW)))
                    ymax = int(min(imH, (boxes[i][2] * imH)))
                    xmax = int(min(imW, (boxes[i][3] * imW)))

                    # Draw bounding box
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)

                    # Draw label
                    label = f'{object_name}: {int(scores[i] * 100)}%'  # Example: 'square: 72%'
                    cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # If both square and triangle are detected, save the image with timestamp and counts
        if square_count > 0 and triangle_count > 0:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            info_text = f"Squares: {square_count}, Triangles: {triangle_count}, Time: {timestamp}"
            cv2.putText(frame, info_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            filename = f"{output_dir}/squares_{square_count}triangles{triangle_count}_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")

        # If a circle is detected, save the image in a separate directory with timestamp
        if circle_detected:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{circle_output_dir}/circle_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Circle detected and saved: {filename}")

        # Display counts of squares and triangles on the frame
        info_text = f"Squares: {square_count}, Triangles: {triangle_count}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Show the frame with detection boxes, labels, and counts
        cv2.imshow('Object Detection', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cv2.destroyAllWindows()
    picam2.stop()

# Set up paths for the model and label map
MODEL_PATH = 'detect77.tflite'  # Path to the .tflite model file
LABEL_PATH = 'labelmap.txt'  # Path to the labelmap.txt file
OUTPUT_DIR = 'captures/detections'  # Directory to save images of squares and triangles
CIRCLE_OUTPUT_DIR = 'captures/hotspots'  # Directory to save images of circles
MIN_CONFIDENCE = 0.9  # Minimum confidence threshold for displaying detection

# Run detection function with PiCamera2
tflite_detect_picamera(MODEL_PATH, LABEL_PATH, OUTPUT_DIR, CIRCLE_OUTPUT_DIR, MIN_CONFIDENCE)

```
