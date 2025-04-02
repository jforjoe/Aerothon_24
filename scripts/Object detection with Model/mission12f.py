import cv2
import numpy as np
import tensorflow as tf
from tensorflow.lite.python.interpreter import Interpreter
from datetime import datetime
import os

# Function to detect squares, triangles, and circles using a TFLite model and webcam
def tflite_detect_webcam(model_path, label_path, output_dir, circle_output_dir, min_conf=0.9):
    # Load label map into memory
    with open(label_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # Load the TensorFlow Lite model into memory
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get model input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height, width = input_details[0]['shape'][1], input_details[0]['shape'][2]

    # Check if model uses float32 inputs and set normalization parameters
    float_input = (input_details[0]['dtype'] == np.float32)
    input_mean, input_std = 127.5, 127.5

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    # Create directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(circle_output_dir, exist_ok=True)

    while cap.isOpened():
        # Capture frame from webcam
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame to match model's input shape
        imH, imW, _ = frame.shape
        image_resized = cv2.resize(frame, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a float model (non-quantized)
        if float_input:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform detection
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[1]['index'])[0]
        classes = interpreter.get_tensor(output_details[3]['index'])[0]
        scores = interpreter.get_tensor(output_details[0]['index'])[0]

        # Initialize counters and flags
        square_count, triangle_count = 0, 0
        circle_detected = False

        # Process each detected object
        for i in range(len(scores)):
            if (scores[i] > min_conf) and (scores[i] <= 1.0):
                object_name = labels[int(classes[i])]  # Lookup object name by class index

                # Count squares and triangles, detect circles
                if object_name == "square":
                    square_count += 1
                elif object_name == "triangle":
                    triangle_count += 1
                elif object_name == "circle":
                    circle_detected = True

                # Draw bounding box and label for each detected object
                if object_name in ["square", "triangle", "circle"]:
                    ymin = int(max(1, (boxes[i][0] * imH)))
                    xmin = int(max(1, (boxes[i][1] * imW)))
                    ymax = int(min(imH, (boxes[i][2] * imH)))
                    xmax = int(min(imW, (boxes[i][3] * imW)))

                    # Draw bounding box
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)

                    # Draw label with confidence percentage
                    label = f'{object_name}: {int(scores[i] * 100)}%'
                    cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Save image with squares and triangles if both are detected
        if square_count > 0 and triangle_count > 0:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            #info_text = f"Squares: {square_count}, Triangles: {triangle_count}, Time: {timestamp}"
            #cv2.putText(frame, info_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            filename = f"{output_dir}/squares_{square_count}triangles{triangle_count}_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")

        # Save image in circle_output_dir if a circle is detected
        if circle_detected:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{circle_output_dir}/circle_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Circle detected and saved: {filename}")

        # Display counts of squares and triangles on the frame
        info_text = f"Squares: {square_count}, Triangles: {triangle_count}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Show frame with detection boxes, labels, and counts
        cv2.imshow('Object Detection', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release webcam and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Set up paths for the model and label map
MODEL_PATH = 'detect77.tflite'  # Path to .tflite model file
LABEL_PATH = 'labelmap.txt'  # Path to labelmap.txt file
OUTPUT_DIR = 'captures/shapes'  # Directory to save images of squares/triangles
CIRCLE_OUTPUT_DIR = 'captures/hotspots'  # Directory to save images of circles
MIN_CONFIDENCE = 0.9  # Minimum confidence threshold

# Run detection function with webcam
tflite_detect_webcam(MODEL_PATH, LABEL_PATH, OUTPUT_DIR, CIRCLE_OUTPUT_DIR, MIN_CONFIDENCE)


