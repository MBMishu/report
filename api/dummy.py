# import torch
# from pathlib import Path
# from PIL import Image
# import matplotlib.pyplot as plt

# model = torch.hub.load('ultralytics/yolov5:v5.0', 'yolov5s', pretrained=False)
# model.load_state_dict(torch.load('E:/Django Project/report/static/models/best.pt'))
# model.eval()

# image_path = 'E:/Django Project/report/static/models/data_1210781.png'

# # Perform object detection on the image
# results = model(image_path)

# # Display the image with bounding boxes around detected objects
# img = Image.open(image_path)
# img.show()

# # Plot the results
# results.show()

# # If you want to save the results to a new image
# results.save(Path('E:/Django Project/report/static/models/detected_image.jpg'))

# # Access the results for further processing
# detected_objects = results.xyxy[0]  # Get bounding box coordinates, labels, and confidence scores

# # Print the detected objects
# print(detected_objects)




from ultralytics import YOLO
from PIL import Image
import os
import cv2

# Load the YOLO model
model = YOLO("E:/Django Project/report/static/models/best.pt")

# Set the path to the video and the output folder
video_path = "E:/Django Project/report/static/b5.mp4"


output_folder = "./frames"

# Open the video capture
cap = cv2.VideoCapture(video_path)

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Process each frame and save every 100th frame
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

count = 0
for frame_index in range(frame_count):
    success, image = cap.read()
    if not success:
        break

    # Save every 100th frame
    if frame_index % 100 == 0:
        frame_filename = f"frame_{count}.jpg"
        frame_path = os.path.join(output_folder, frame_filename)
        cv2.imwrite(frame_path, image)
        
        # Perform object detection on the saved frame
        pil_image = Image.open(frame_path)
        results_list = model.predict(source=[pil_image], save=True)
        
        # Optionally, you can use the results_list for further processing

        count += 1

# Release the video capture
cap.release()
