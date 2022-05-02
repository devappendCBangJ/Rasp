import cv2 as cv
import numpy as np
import RPi.GPIO as GPIO
import sys
import time
import serial

#ser = serial.Serial('/dev/ttyUSB1',115200)#ACM
#ser = serial.Serial('/dev/ttyUSB0',115200)

curTime = time.time()
prevTime = curTime
sec = curTime - prevTime
threshold_su= 110
threshold_vu = 110
threshold__sd = 110
threshold_vd = 110
hsv = 0
area = 0
lower_blue1 = 0
upper_blue1 = 0
lower_blue2 = 0
upper_blue2 = 0
lower_blue3 = 0
upper_blue3 = 0
dirr =0
start_step = 0
def nothing(x):
    pass

def mouse_callback(event, x, y, flags, param):
    global area,threshold_su,threshold_vu,threshold__sd,threshold_vd, hsv, lower_blue1, upper_blue1, lower_blue2, upper_blue2, lower_blue3, upper_blue3
    
    if event == cv.EVENT_LBUTTONDOWN:
        print(img_color[y, x])
        color = img_color[y, x]

        one_pixel = np.uint8([[color]])
        hsv = cv.cvtColor(one_pixel, cv.COLOR_BGR2HSV)
        hsv = hsv[0][0]
        print(hsv)
        threshold_su= cv.getTrackbarPos('threshold_su', 'img_result')
        threshold_vu = cv.getTrackbarPos('threshold_vu', 'img_result')
        threshold__sd = cv.getTrackbarPos('threshold__sd', 'img_result')
        threshold_vd = cv.getTrackbarPos('threshold_vd', 'img_result')
        # HSV 색공간에서 마우스 클릭으로 얻은 픽셀값과 유사한 필셀값의 범위를 정합니다.
        if hsv[0] < 10:
            print("case1")
            lower_blue1 = np.array([hsv[0]-10+180, threshold_su, threshold_vu])
            upper_blue1 = np.array([180, threshold__sd, threshold_vd])
            lower_blue2 = np.array([0, threshold_su, threshold_vu])
            upper_blue2 = np.array([hsv[0], threshold__sd, threshold_vd])
            lower_blue3 = np.array([hsv[0], threshold_su, threshold_vu])
            upper_blue3 = np.array([hsv[0]+10, threshold__sd, threshold_vd])
            #     print(i-10+180, 180, 0, i)
            #     print(i, i+10)

        elif hsv[0] > 170:
            print("case2")
            lower_blue1 = np.array([hsv[0], threshold_su, threshold_vu])
            upper_blue1 = np.array([180, threshold__sd, threshold_vd])
            lower_blue2 = np.array([0, threshold_su, threshold_vu])
            upper_blue2 = np.array([hsv[0]+10-180, threshold__sd, threshold_vd])
            lower_blue3 = np.array([hsv[0]-10, threshold_su, threshold_vu])
            upper_blue3 = np.array([hsv[0], threshold__sd, threshold_vd])
            #     print(i, 180, 0, i+10-180)
            #     print(i-10, i)
        else:
            print("case3")
            lower_blue1 = np.array([hsv[0], threshold_su, threshold_vu])
            upper_blue1 = np.array([hsv[0]+10, threshold__sd, threshold_vd])
            lower_blue2 = np.array([hsv[0]-10, threshold_su, threshold_vu])
            upper_blue2 = np.array([hsv[0], threshold__sd, threshold_vd])
            lower_blue3 = np.array([hsv[0]-10, threshold_su, threshold_vu])
            upper_blue3 = np.array([hsv[0], threshold__sd, threshold_vd])
            #     print(i, i+10)
            #     print(i-10, i)

        print(hsv[0])
        
        print("@1", lower_blue1, "~", upper_blue1)
        print("@2", lower_blue2, "~", upper_blue2)
        print("@3", lower_blue3, "~", upper_blue3)


cv.namedWindow('img_color')#창열기
cv.setMouseCallback('img_color', mouse_callback)#마우스 클릭시 좌표, 클릭인지 움직임지 등등 이벤트를 함수에 전달

# 카메라 설정, 사이즈 설정
# cap = cv.VideoCapture(cv.CAP_DSHOW + 1)
cap = cv.VideoCapture(0, cv.CAP_V4L2)
cap.set(3,320)
cap.set(4,240)
cv.namedWindow('img_result')

areavs=0
area=0
centervsX=-10
centervsY=-10

cv.createTrackbar('threshold_su', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('threshold_su', 'img_result', 120)
cv.createTrackbar('threshold_vu', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('threshold_vu', 'img_result', 120)
cv.createTrackbar('threshold__sd', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('threshold__sd', 'img_result', 120)
cv.createTrackbar('threshold_vd', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('threshold_vd', 'img_result', 120)
while(True):
    curTime = time.time()
    sec = curTime - prevTime
    fps = 1/sec

    # 카메라 읽기
    ret,img_color = cap.read()
    # img_color = cv.resize(img_color, dsize=(320, 240), interpolation=cv.INTER_AREA)

    # hsv 변환, 마스크 형성, 노이즈 제거, 특징 추출
    img_hsv = cv.cvtColor(img_color, cv.COLOR_BGR2HSV)

    img_mask1 = cv.inRange(img_hsv, lower_blue1, upper_blue1)
    img_mask2 = cv.inRange(img_hsv, lower_blue2, upper_blue2)
    img_mask3 = cv.inRange(img_hsv, lower_blue3, upper_blue3)
    img_mask = img_mask1 | img_mask2 | img_mask3

    kernel = np.ones((5,5), np.uint8)
    img_mask = cv.morphologyEx(img_mask, cv.MORPH_OPEN, kernel)
    img_mask = cv.morphologyEx(img_mask, cv.MORPH_CLOSE, kernel)

    img_result = cv.bitwise_and(img_color, img_color, mask=img_mask)
    numOfLabels, img_label, stats, centroids = cv.connectedComponentsWithStats(img_mask)

    # 특징 전처리
    areavs=0
    for idx, centroid in enumerate(centroids):
        if stats[idx][0] == 0 and stats[idx][1] == 0:
            continue
        if np.any(np.isnan(centroid)):
            continue
        x, y, width, height, area = stats[idx]
        
        centerX, centerY = int(centroid[0]), int(centroid[1])
        if area >areavs:
            xvs = x
            widthvs = width
            areavs = area
            centervsX_R=centerX
            centervsY_R=centerY

    # 결과 연산
    if stats[idx][0] != 0 or stats[idx][1] != 0:
        cv.circle(img_color, (centervsX_R, centervsY_R), 10, (0, 0, 255), 10)
        print('/fps : ', fps, '/areavs : ', areavs, '/centervsX_R : ', centervsX_R, '/centervsY_R : ', centervsY_R)
    
    # 시각화
    cv.imshow('img_color', img_color)
    cv.imshow('img_mask', img_mask)
    cv.imshow('img_result', img_result)

    # 카메라 종료 조건
    if cv.waitKey(1) & 0xFF == 27:
        break
    prevTime = curTime

cap.release()
cv.destroyAllWindows()