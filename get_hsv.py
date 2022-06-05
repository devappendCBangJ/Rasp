import time
import serial
import cv2
import numpy as np
import RPi.GPIO as GPIO
font, LT = cv2.FONT_HERSHEY_SIMPLEX,cv2.LINE_AA
text1 = 'Press ESC to extract Green'
text2 = 'Press ESC to extract Blue'
text3 = 'Press ESC to extract Red'

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
W_View_size = 400
H_View_size = 300

while True:
    ret, frame1 = cap.read()
    frame = cv2.resize(frame1, dsize=(W_View_size, H_View_size), interpolation=cv2.INTER_AREA)
    if not ret:
        continue
    cv2.putText(frame1,text1,(20,20), font,0.5,(0,255,255),0,LT)
    cv2.imshow('frame',frame1)
    k = cv2.waitKey(5) & 0xFF
    if k == 27: # ESC key
        break
roi=cv2.selectROI('frame',frame1)
roi_bgr=frame1[roi[1]:roi[1] + roi[3],roi[0]:roi[0] + roi[2]]
roi_hsv=cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
temp=cv2.split(roi_hsv)
minmax=[]
for c in temp:
    mm = cv2.minMaxLoc(c) # mm: (min, max, minLoc, maxLoc)
    minmax.append(mm[:2])
lower1=np.array([e[0] for e in minmax], dtype=np.uint8)
upper1=np.array([e[1] for e in minmax], dtype=np.uint8)

while True:
    _, frame2 = cap.read()
    cv2.putText(frame2, text2, (20, 20), font, 0.5, (0, 255, 255), 0, LT)
    cv2.imshow('frame', frame2)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:  # ESC key
        break
roi = cv2.selectROI('frame', frame2)
roi_bgr = frame2[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
temp = cv2.split(roi_hsv)
minmax = []
for c in temp:
    mm = cv2.minMaxLoc(c)  # mm: (min, max, minLoc, maxLoc)
    minmax.append(mm[:2])
lower2 = np.array([e[0] for e in minmax], dtype=np.uint8)
upper2 = np.array([e[1] for e in minmax], dtype=np.uint8)

while True:
    _, frame3 = cap.read()
    cv2.putText(frame3, text3, (20, 20), font, 0.5, (0, 255, 255), 0, LT)
    cv2.imshow('frame', frame3)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:  # ESC key
        break
roi = cv2.selectROI('frame', frame3)
roi_bgr = frame3[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
temp = cv2.split(roi_hsv)
minmax = []
for c in temp:
    mm = cv2.minMaxLoc(c)  # mm: (min, max, minLoc, maxLoc)
    minmax.append(mm[:2])
lower3 = np.array([e[0] for e in minmax], dtype=np.uint8)
upper3 = np.array([e[1] for e in minmax], dtype=np.uint8)

print('첫번째')
print(lower1)
print(upper1)

print('2번째')
print(lower2)
print(upper2)

print('3번째')
print(lower3)
print(upper3)

while True:
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #lower_blue = np.array([110,50,50])
    #upper_blue = np.array([130,255,255])
    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask3 = cv2.inRange(hsv, lower3, upper3)
    mask = mask1|mask2|mask3
    res = cv2.bitwise_and(frame,frame,mask=mask)
    res2=np.hstack((frame,res))
    cv2.imshow('mask',mask)
    cv2.imshow('img & res',res2)
    k = cv2.waitKey(5) & 0xFF
    if k == 27: # ESC key
        break
cv2.destroyAllWindows()
