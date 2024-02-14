import cv2
import numpy as np

# Read the underwater image
underwater_image = cv2.imread('E:/Django Project/report/media/frames/120_frame_0.jpg')

# Increase blue channel to reduce green color cast
underwater_image[:,:,0] = cv2.addWeighted(underwater_image[:,:,0], 1.2, np.zeros_like(underwater_image[:,:,0]), 0, 0)
# Reduce green channel to compensate for the increased blue
underwater_image[:,:,1] = cv2.addWeighted(underwater_image[:,:,1], 0.8, np.zeros_like(underwater_image[:,:,1]), 0, 0)

# Display the images
cv2.imshow('Original', underwater_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
