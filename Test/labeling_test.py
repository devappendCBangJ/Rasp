import cv2 as cv
import numpy as np
import time

curTime=0
prevTime=0
FPS=list()

cap = cv.VideoCapture(0,cv.CAP_V4L2)  # 객체선언 cap = cv.VideoCapture(0, cv.CAP_V4L2)
cap.set(3, 320)  # 가로사이즈 320
cap.set(4, 240)  # 세로사이즈 240
centerX_b = 0
centerY_b = 0
centerX_r = 0
centerY_r = 0
centerX_g = 0
centerY_g = 0
dir = 2             # 물체 왼쪽 dir =-1, 가운데 dir =0 , 물체 오른쪽 = 1, 감지 안됨 =0
inc = 3
count = 0
while (True):
    curTime = time.time()
    sec = curTime - prevTime
    fps = 1/sec
    FPS.append(fps)
    count=count+1
    if(count==50):
        print(np.mean(FPS))
        FPS=[]
        count=0
    ret, img_color = cap.read()  # frame 가로 *세로 *3 으로 표현 ==> 카메라 값 읽어 들이기
    img_hsv = cv.cvtColor(img_color, cv.COLOR_BGR2HSV)  # hsv 컬러 변환
    lower_green = (36, 72, 78)
    upper_green = (70, 255, 219)
    lower_red = (170, 109, 130)
    upper_red = (175, 235, 230)
    lower_red_or = (0, 109, 130)
    upper_red_or = (10, 235, 230)
    lower_blue = (108, 107, 134)
    upper_blue = (119, 196, 215)

    img_mask_red = cv.inRange(img_hsv, lower_red, upper_red)
    img_mask_red_or = cv.inRange(img_hsv, lower_red_or, upper_red_or)
    img_mask_redSum = img_mask_red | img_mask_red_or
    img_mask_b = cv.inRange(img_hsv, lower_blue, upper_blue)
    img_mask_g = cv.inRange(img_hsv, lower_green, upper_green)
    img_mask_t = img_mask_redSum | img_mask_b | img_mask_g

    kernel = np.ones((5, 5), np.uint8)  # 모폴로지  노이즈 필터링

    img_mask_redSum = cv.morphologyEx(img_mask_redSum, cv.MORPH_OPEN, kernel)
    img_mask_redSum = cv.morphologyEx(img_mask_redSum, cv.MORPH_CLOSE, kernel)
    img_mask_b = cv.morphologyEx(img_mask_b, cv.MORPH_OPEN, kernel)
    img_mask_b = cv.morphologyEx(img_mask_b, cv.MORPH_CLOSE, kernel)
    img_mask_g = cv.morphologyEx(img_mask_g, cv.MORPH_OPEN, kernel)
    img_mask_g = cv.morphologyEx(img_mask_g, cv.MORPH_CLOSE, kernel)

    _, _, stats_r, centroids_r = cv.connectedComponentsWithStats(img_mask_redSum)
    max_centerX_r = 0
    max_centerY_r = 0
    max_area_r = 0
    for idx, centroid in enumerate(centroids_r):  # 한 row씩만 뽑아줌
        if stats_r[idx][0] == 0 and stats_r[idx][1] == 0:  # roi 이미지가 없으면 pass
            dir = 2
            continue
        if np.any(np.isnan(centroid)):  # ????
            continue
        x, y, width, height, area = stats_r[idx]  # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
        centerX_r, centerY_r = int(centroid[0]), int(centroid[1])
        if (area > max_area_r):                       # 가장 큰 영역을 선별
            max_area_r = area
            max_centerX_r = centerX_r
            max_centerY_r = centerY_r
    if max_area_r > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
        cv.circle(img_color, (max_centerX_r, max_centerY_r), 10, (0, 0, 255), 10)
        if max_centerX_r <120 :
            dir = 1
        elif (120<max_centerX_r<200):
            dir = 0       #가운데
        else:
            dir = -1      #왼쪽


    max_centerX_b = 0
    max_centerY_b = 0
    max_area_b = 0

    _, _, stats_b, centroids_b = cv.connectedComponentsWithStats(img_mask_b)
    for idx, centroid in enumerate(centroids_b):  # 한 row씩만 뽑아줌
        if stats_b[idx][0] == 0 and stats_b[idx][1] == 0:  # roi 이미지가 없으면 pass
            continue
            dir = 2
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
            dir =1
        elif (120 < max_centerX_b < 200):
            dir = 0 # 가운데
        else:
            dir = -1

    max_centerX_g = 0
    max_centerY_g = 0
    max_area_g = 0

    _, _, stats_g, centroids_g = cv.connectedComponentsWithStats(img_mask_g)
    for idx, centroid in enumerate(centroids_g):  # 한 row씩만 뽑아줌
        if stats_g[idx][0] == 0 and stats_g[idx][1] == 0:  # roi 이미지가 없으면 pass
            dir = 2
            continue
        if np.any(np.isnan(centroid)):  # ????

            continue
        x, y, width, height, area = stats_g[idx]  # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
        centerX_g, centerY_g = int(centroid[0]), int(centroid[1])  # centerX, centerY = int(centroid[0]), int(centroid[1])??
        if (area > max_area_g):
            max_area_g = area
            max_centerX_g = centerX_g
            max_centerY_g = centerY_g
    if max_area_g > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
        cv.circle(img_color, (max_centerX_g, max_centerY_g), 10, (0, 0, 255), 10)
        if 0 < max_centerX_g < 120:
            dir = 1
        elif (120 < max_centerX_g < 200):
            dir = 0  # 가운데
        else:
            dir = -1
    
    cv.imshow('img_color', img_color)
    cv.imshow('img_mask_t', img_mask_t)
    prevTime = curTime
    if cv.waitKey(1) & 0xFF == 27:
        break

    
cv.destroyAllWindows()