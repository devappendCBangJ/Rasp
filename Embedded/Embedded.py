import cv2 as cv
import numpy as np
import time as t
import serial

cap = cv.VideoCapture(0, cv.CAP_V4L2)  # 객체선언 cap = cv.VideoCapture(0, cv.CAP_V4L2)
cap.set(3, 320)  # 가로사이즈 320
cap.set(4, 240)  # 세로사이즈 240
centerX_b = 0
centerX_r = 0
centerX_g = 0
centerY_g = 0
centerY_b = 0
centerY_r = 0

mode = 2

ser = serial.Serial('/dev/ttyAMA1', baudrate=115200, timeout=1)
if ser.isOpen() == False:
    ser.open()                             # 통신 포트 열어 줌
while (True):
    state_data = "0"
    ret, img_color = cap.read()  # frame 가로 *세로 *3 으로 표현 ==> 카메라 값 읽어 들이기

    img_hsv = cv.cvtColor(img_color, cv.COLOR_BGR2HSV)  # hsv 컬러 변환

    '''if ser.readable():
        mode = ser.readline()'''

    lower_green = (40, 100, 9)
    upper_green = (65, 255, 255)
    lower_red = (160, 111, 110)
    upper_red = (180, 255, 255)
    lower_red_or = (0, 111, 110)
    upper_red_or = (10, 255, 255)
    lower_blue = (100, 82, 61)
    upper_blue = (130, 221, 255)

    if mode == 1:  # 빨강 색
        img_mask_red = cv.inRange(img_hsv, lower_red, upper_red)
        img_mask_red_or = cv.inRange(img_hsv, lower_red_or, upper_red_or)
        img_mask_redSum = img_mask_red | img_mask_red_or
        img_mask_t = img_mask_redSum
        kernel = np.ones((3, 3), np.uint8)  # 모폴로지  노이즈 필터링
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_OPEN, kernel)
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_CLOSE, kernel)
        _, _, stats_r, centroids_r = cv.connectedComponentsWithStats(img_mask_redSum)

        max_centerX_r = 0
        max_centerY_r = 0
        max_area_r = 0
        for idx, centroid in enumerate(centroids_r):  # 한 row씩만 뽑아줌
            if stats_r[idx][0] == 0 and stats_r[idx][1] == 0:  # roi 이미지가 없으면 pass
                continue
            if np.any(np.isnan(centroid)):  # ????
                state_data = "0"
                continue
            x, y, width, height, area = stats_r[idx]  # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
            centerX_r, centerY_r = int(centroid[0]), int(centroid[1])
            if (area > max_area_r):                       # 가장 큰 영역을 선별
                max_area_r = area
                max_centerX_r = centerX_r
                max_centerY_r = centerY_r
        if max_area_r > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
            cv.circle(img_color, (max_centerX_r, max_centerY_r), 10, (0, 0, 255), 10)
            #cv.rectangle(img_color, (x, y), (x + width, y + height), (0, 0, 255))
            if max_centerX_r <120 :
                state_data += ",R"
            elif (120<max_centerX_r<200):
                state_data += ",M"       #가운데
            else:
                state_data += ",L"        #왼쪽
            if max_area_r > 30000:
                state_data= state_data.replace('0', '1')
            ser.write(state_data)
            print(state_data)
    max_centerX_b = 0
    max_centerY_b = 0
    max_area_b = 0
    if mode == 2:  # 파란색
        img_mask_t = cv.inRange(img_hsv, lower_blue, upper_blue)

        kernel = np.ones((3, 3), np.uint8)  # 모폴로지  노이즈 필터링
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_OPEN, kernel)
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_CLOSE, kernel)
        _, _, stats_b, centroids_b = cv.connectedComponentsWithStats(img_mask_t)

        for idx, centroid in enumerate(centroids_b):  # 한 row씩만 뽑아줌
            if stats_b[idx][0] == 0 and stats_b[idx][1] == 0:  # roi 이미지가 없으면 pass
                continue
            if np.any(np.isnan(centroid)):  # ????
                state_data = "0"
                continue
            x, y, width, height, area = stats_b[idx]  # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
            centerX_b, centerY_b = int(centroid[0]), int(centroid[1])

            if (area > max_area_b):
                max_area_b = area
                max_centerX_b = centerX_b
                max_centerY_b = centerY_b

        if max_area_b > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
            cv.circle(img_color, (max_centerX_b, max_centerY_b), 10, (0, 0, 255), 10)
            #cv.rectangle(img_color, (x, y), (x + width, y + height), (0, 0, 255))
            if 0<max_centerX_b < 120:
                state_data += ",R"
            elif (120 < max_centerX_b < 200):
                state_data += ",M"  # 가운데
            else:
                state_data += ",L"  # 왼쪽
            if max_area_b > 30000:
                state_data = state_data.replace('0', '1')
            ser.write(b'state_data')
            print(state_data)

    max_centerX_g = 0
    max_centerY_g = 0
    max_area_g = 0
    if mode == 3:  # 초록색
        img_mask_t = cv.inRange(img_hsv, lower_green, upper_green)
        kernel = np.ones((3, 3), np.uint8)  # 모폴로지  노이즈 필터링
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_OPEN, kernel)
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_CLOSE, kernel)
        _, _, stats_g, centroids_g = cv.connectedComponentsWithStats(img_mask_t)
        for idx, centroid in enumerate(centroids_g):  # 한 row씩만 뽑아줌
            if stats_g[idx][0] == 0 and stats_g[idx][1] == 0:  # roi 이미지가 없으면 pass
                continue
            if np.any(np.isnan(centroid)):  # ????
                state_data = "0"
                continue
            x, y, width, height, area = stats_g[idx]  # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
            centerX_g, centerY_g = int(centroid[0]), int(centroid[1])  # centerX, centerY = int(centroid[0]), int(centroid[1])??
            if (area > max_area_g):
                max_area_g = area
                max_centerX_g = centerX_g
                max_centerY_g = centerY_g
        if max_area_g > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
            cv.circle(img_color, (max_centerX_g, max_centerY_g), 10, (0, 0, 255), 10)
            #cv.rectangle(img_color, (x, y), (x + width, y + height), (0, 0, 255))
            if 0< max_centerX_g < 120:
                state_data += ",R"
            elif (120 < max_centerX_g < 200):
                state_data += ",M"  # 가운데
            else:
                state_data += ",L"  # 왼쪽
            if max_centerX_g > 30000:
                state_data = state_data.replace('0', '1')
            ser.write(b'state_data')

    print(state_data)
    cv.imshow('img_color', img_color)
    cv.imshow('img_mask_t', img_mask_t)
    if cv.waitKey(1) & 0xFF == 27:
        break

cv.destroyAllWindows()
