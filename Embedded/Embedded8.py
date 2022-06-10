import cv2 as cv
import numpy as np
import time as t
import serial

cap = cv.VideoCapture(0, cv.CAP_V4L2)
cap.set(3, 320)  # 가로사이즈 320
cap.set(4, 240)  # 세로사이즈 240
centerX_b = 0
centerY_b = 0
centerX_g = 0
centerY_g = 0
centerX_r = 0
centerY_r = 0

##################잡았냐 안잡았냐, 색깔 인식 모드, ######################
isGraped = "0"  # isGraped = 0 : 안잡음, isGraped = 1 : 잡음
isColored = 0  # 색깔이 입력 됬나
colorMode = 0  # colorMode = 1 : 빨 colorMode = 2 :파  colorMode = 3 :초
isEnd = 0  # 안끝났음 isEnd =1 끝났음
servo_stop = "0"
rx=''

################ hsv night##################################################
# lower_green = (56, 72, 69)
# upper_green = (76, 255, 255)
# lower_red = (163, 178, 104)
# upper_red = (180, 255, 255)
# lower_red_or = (0, 178, 104)
# upper_red_or = (3, 255, 255)
# lower_blue = (96, 74, 73)
# upper_blue = (116, 255, 255)
######################################################################
lower_green = (56, 72, 69)
upper_green = (76, 255, 255)
lower_red = (163, 178, 104)
upper_red = (180, 255, 255)
lower_red_or = (0, 178, 104)
upper_red_or = (3, 255, 255)
lower_blue = (96, 74, 73)
upper_blue = (116, 255, 255)
max_area_which = 0
max_centerX_which = 0
max_centerY_which = 0


######################################################################
def which_color():  # 어떤 컬러가 포착 됬는지
    global isColored
    global colorMode
    global state_data
    global servo_stop
    state_data = "9,9,9"
    img_hsv_which = img_hsv[:, 150:170]
    img_mask_red = cv.inRange(img_hsv_which, lower_red, upper_red)
    img_mask_red_or = cv.inRange(img_hsv_which, lower_red_or, upper_red_or)
    img_mask_redSum = img_mask_red | img_mask_red_or
    img_mask_b = cv.inRange(img_hsv_which, lower_blue, upper_blue)
    kernel = np.ones((7, 7), np.uint8)
    img_mask_redSum = cv.morphologyEx(img_mask_redSum, cv.MORPH_OPEN, kernel)
    img_mask_redSum = cv.morphologyEx(img_mask_redSum, cv.MORPH_CLOSE, kernel)
    img_mask_b = cv.morphologyEx(img_mask_b, cv.MORPH_OPEN, kernel)
    img_mask_b = cv.morphologyEx(img_mask_b, cv.MORPH_CLOSE, kernel)
    _, _, stats_r, centroids_r = cv.connectedComponentsWithStats(img_mask_redSum)
    for idx, centroid_r in enumerate(centroids_r):  # 한 row씩만 뽑아줌
        if stats_r[idx][0] == 0 and stats_r[idx][1] == 0:  # roi 이미지가 없으면 pass
            continue
        if np.any(np.isnan(centroid_r)):
            continue
        _, _, _, _, area_r = stats_r[idx]  # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
        if area_r > 500:  # 크기가 80 이상이면 동그라미, 사각형인정
            state_data = "1,9,9"
            t.sleep(1.5)
            isColored = 1
            colorMode = 1
            break
    _, _, stats_b, centroids_b = cv.connectedComponentsWithStats(img_mask_b)
    for idx, centroid_b in enumerate(centroids_b):  # 한 row씩만 뽑아줌
        if stats_b[idx][0] == 0 and stats_b[idx][1] == 0:  # roi 이미지가 없으면 pass
            continue
        if np.any(np.isnan(centroid_b)):
            continue
        _, _, _, _, area_b = stats_b[idx]  # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
        if area_b > 500:  # 크기가 80 이상이면 동그라미, 사각형인정
            state_data = "1,9,9"
            t.sleep(1.5)
            isColored = 1
            colorMode = 2
            break




########################################
ser = serial.Serial('/dev/ttyAMA1', baudrate=115200, timeout=0)
if ser.isOpen() == False:
    ser.open()  # 통신 포트 열어 줌
######################################################################
while (True):
    state_data = "9"  # 서보모터 다시 움직여라 신호     #state_data (물체의 방향(왼쪽 0, 가운데 1, 오른쪽 2), 크기(작음 : 0,정렬 : 1,잡아 : 2), 9)
    ret, img_color = cap.read()  # frame 가로 *세로 *3 으로 표현 ==> 카메라 값 읽어 들이기
    height, width = img_color.shape[:2]
    img_color = cv.resize(img_color, (width, height), interpolation=cv.INTER_AREA)
    img_hsv = cv.cvtColor(img_color, cv.COLOR_BGR2HSV)  # hsv 컬러 변환

    ########################색 입력 ########################################
    if isColored == 0 and isGraped == "0":
        which_color()

    if ser.readable():
        ser.timeout = 0
        rx = ser.read().decode()
        if (rx == '1'):
            isGraped="1"
    print(isGraped)
    ############################ 색깔 빨강 #################################
    max_centerX_r = 0
    max_centerY_r = 0
    max_area_r = 0
    if colorMode == 1 and isColored == 1 and isGraped == "0":  # 빨강 색
        img_mask_red = cv.inRange(img_hsv, lower_red, upper_red)
        img_mask_red_or = cv.inRange(img_hsv, lower_red_or, upper_red_or)
        img_mask_redSum = img_mask_red | img_mask_red_or
        img_mask_t = img_mask_redSum
        kernel = np.ones((5, 5), np.uint8)  # 모폴로지  노이즈 필터링
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_OPEN, kernel)
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_CLOSE, kernel)

        _, _, stats_r, centroids_r = cv.connectedComponentsWithStats(img_mask_redSum)
        for idx, centroid in enumerate(centroids_r):  # 한 row씩만 뽑아줌
            if stats_r[idx][0] == 0 and stats_r[idx][1] == 0:  # roi 이미지가 없으면 pass
                continue
            if np.any(np.isnan(centroid)):  # ????
                continue
            x, y, width, height, area = stats_r[idx]  # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
            centerX_r, centerY_r = int(centroid[0]), int(centroid[1])
            if (area > max_area_r):  # 가장 큰 영역을 선별
                max_area_r = area
                max_centerX_r = centerX_r
                max_centerY_r = centerY_r
        if max_area_r > 100:  # 크기가 80 이상이면 동그라미, 사각형인정
            cv.circle(img_color, (max_centerX_r, max_centerY_r), 10, (0, 0, 255), 10)
            # cv.rectangle(img_color, (x, y), (x + width, y + height), (0, 0, 255))
            if max_centerX_r < 135:
                state_data = "0"
            elif (135 < max_centerX_r < 185):
                state_data = "1"  # 가운데
            else:
                state_data = "2"  # 왼쪽

            if max_area_r > 1000:
                state_data += ",1"
            else:
                state_data += ",0"
            if max_area_r > 2500:
                charactor = list(state_data)
                charactor[2] = '2'
                state_data = "".join(charactor)
        else:
            state_data += ",9"
    ############################색깔 파랑 #################################
    max_centerX_b = 0
    max_centerY_b = 0
    max_area_b = 0
    if colorMode == 2 and isColored == 1 and isGraped == "0":  # 파란색
        img_mask_t = cv.inRange(img_hsv, lower_blue, upper_blue)
        kernel = np.ones((5, 5), np.uint8)  # 모폴로지  노이즈 필터링
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_OPEN, kernel)
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_CLOSE, kernel)
        _, _, stats_b, centroids_b = cv.connectedComponentsWithStats(img_mask_t)

        for idx, centroid in enumerate(centroids_b):  # 한 row씩만 뽑아줌
            if stats_b[idx][0] == 0 and stats_b[idx][1] == 0:  # roi 이미지가 없으면 pass
                continue
            if np.any(np.isnan(centroid)):  # ????
                continue
            x, y, width, height, area = stats_b[idx]  # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
            centerX_b, centerY_b = int(centroid[0]), int(centroid[1])

            if (area > max_area_b):
                max_area_b = area
                max_centerX_b = centerX_b
                max_centerY_b = centerY_b

        if max_area_b > 100:  # 크기가 80 이상이면 동그라미, 사각형인정
            cv.circle(img_color, (max_centerX_b, max_centerY_b), 10, (0, 0, 255), 10)
            if max_centerX_b < 135:
                state_data = "0"
            elif (135 < max_centerX_b < 185):
                state_data = "1"  # 가운데
            else:
                state_data = "2"  # 왼쪽

            if max_area_b > 1000:  # 크기 커지면 두번째 데이터 추가
                state_data += ",1"
            else:
                state_data += ",0"

            if max_area_b > 2500:
                charactor = list(state_data)
                charactor[2] = '2'
                state_data = "".join(charactor)
        else:
            state_data += ",9"
    ###########################3 색깔 초록 #################################
    max_centerX_g = 0
    max_centerY_g = 0
    max_area_g = 0
    if isGraped == "1":
        img_mask_t = cv.inRange(img_hsv, lower_green, upper_green)
        kernel = np.ones((5, 5), np.uint8)  # 모폴로지  노이즈 필터링
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_OPEN, kernel)
        img_mask_t = cv.morphologyEx(img_mask_t, cv.MORPH_CLOSE, kernel)
        _, _, stats_g, centroids_g = cv.connectedComponentsWithStats(img_mask_t)
        for idx, centroid in enumerate(centroids_g):  # 한 row씩만 뽑아줌
            if stats_g[idx][0] == 0 and stats_g[idx][1] == 0:  # roi 이미지가 없으면 pass
                continue
            if np.any(np.isnan(centroid)):  # ????
                continue
            x, y, width, height, area = stats_g[idx]
            centerX_g, centerY_g = int(centroid[0]), int(centroid[1])
            if (area > max_area_g):
                max_area_g = area
                max_centerX_g = centerX_g
                max_centerY_g = centerY_g
        if max_area_g > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
            cv.circle(img_color, (max_centerX_g, max_centerY_g), 10, (0, 0, 255), 10)
            if max_centerX_g < 135:
                state_data = "0"
            elif (135 < max_centerX_g < 185):
                state_data = "1"  # 가운데
            else:
                state_data = "2"  # 왼쪽
            if max_area_g > 1000:
                state_data += ",1"
            else:
                state_data += ",0"
            if max_area_g > 2000:
                charactor = list(state_data)
                charactor[2] = '2'
                state_data = "".join(charactor)
        else:
            state_data += ",9"

    if colorMode != 0:
        state_data += ",9"
    state_data += "/"
    #print(max_area_g, state_data)
    ser.write(bytes(state_data, encoding='ascii'))
    cv.imshow('img_color0', img_color)

    if isColored == 0:
        cv.imshow('img_color', img_color[0])
    if isColored != 0:
        cv.imshow('img_mask_t', img_mask_t)

    if cv.waitKey(1) & 0xFF == 27:
        break

cv.destroyAllWindows()

