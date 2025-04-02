import cv2
import numpy as np
import pytesseract


frame = cv2.imread('Objects/Hotspot 2-01.png')  # Load example image

# Specify the desired dimensions (width, height)
new_width = 640
new_height = 640

# Resize the image
frame = cv2.resize(frame, (new_width, new_height))

# Define red color range (adjust these values as needed)
lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

# Convert the frame to HSV color space and apply color mask
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_red, upper_red)
res = cv2.bitwise_and(frame, frame, mask=mask)

# Find contours on the red mask
contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

'''
# Process each contour to detect circular shapes
for cnt in contours:
    # Approximate the contour and check circularity
    perimeter = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)

    # Check if the contour is circular based on aspect ratio or circularity
    if len(approx) > 8:  # A higher number indicates a more circular shape
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        center = (int(x), int(y))
        radius = int(radius)

        # Draw the circle
        cv2.circle(frame, center, radius, (0, 255, 0), 2)
'''

# Draw contours on the image
for cnt in contours:
    # Draw the contour
    cv2.drawContours(frame, [cnt], 0, (0, 255, 0), 2)

    # Calculate contour properties
    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)
    (x, y), radius = cv2.minEnclosingCircle(cnt)
    center = (int(x), int(y))
    radius = int(radius)  


    # Print information about the contour
    print(f"Area: {area}, Perimeter: {perimeter}, Center: {center}, Radius: {radius}")

# Display the image with contours
cv2.imshow("Image with Contours", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
