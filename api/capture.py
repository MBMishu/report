import os
import cv2

count = 0

cap = cv2.VideoCapture('E:/Django Project/report/static/b5.mp4')
success,image = cap.read()

if not os.path.exists('./frames'):
    os.mkdir('./frames')
    
while success:
    success,image =cap.read()
    
    if not success:
        break
    cv2.imwrite('./frames/'+str(count)+'.jpg',image)
    
    if cv2.waitKey(10) == 27:
        break
    count += 1
        