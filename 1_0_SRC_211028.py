import cv2 as cv
import numpy as np
import serial
import time

ser = serial.Serial('/dev/ttyAMA1', 115200)

# ------- state 정의 -------------------------
# 빨간색 영역이 왼쪽에 위치    : 'L'
# 빨간색 영역이 오른쪽에 위치  : 'R'
# 빨간색 영역이 양쪽에 위치    : 'M'
# 파란색 영역이 왼쪽에 위치    : 'L'
# 파란색 영역이 오른쪽에 위치  : 'R'
# 파란색 영역이 양쪽에 위치    : 'M'
# 로봇이 전방 좌측 방향에 위치 : 'l'
# 로봇이 전방 중앙에 위치     : 'm'
# 로봇이 전방 우측 방향에 위치 : 'r'
# 로봇이 없음 :               'n'
# *전략에 따라 추가 요망*
# -------------------------------------------

cap0 = cv.VideoCapture('/dev/video0', cv.CAP_V4L2)
# cap1 = cv.VideoCapture('/dev/video1', cv.CAP_V4L2)
main_cap = cap0
# 폭, 너비 설정
width = 240
height = 180

erase_noise_area = 70
battle_mode_area = 1000


# mask 를 위한 기준 값 설정 함수

def masking(img_hsv, hsv, threshold):
    if hsv < 10:
        lower1 = np.array([hsv - 10 + 180, threshold, threshold])
        upper1 = np.array([180, 255, 255])
        lower2 = np.array([0, threshold, threshold])
        upper2 = np.array([hsv, 255, 255])
        lower3 = np.array([hsv, threshold, threshold])
        upper3 = np.array([hsv + 10, 255, 255])
    elif hsv > 170:
        lower1 = np.array([hsv, threshold, threshold])
        upper1 = np.array([180, 255, 255])
        lower2 = np.array([0, threshold, threshold])
        upper2 = np.array([hsv + 10 - 180, 255, 255])
        lower3 = np.array([hsv - 10, threshold, threshold])
        upper3 = np.array([hsv, 255, 255])
    else:
        lower1 = np.array([hsv, threshold, threshold])
        upper1 = np.array([hsv + 10, 255, 255])
        lower2 = np.array([hsv - 10, threshold, threshold])
        upper2 = np.array([hsv, 255, 255])
        lower3 = np.array([hsv - 10, threshold, threshold])
        upper3 = np.array([hsv, 255, 255])

    img_mask1 = cv.inRange(img_hsv, lower1, upper1)
    img_mask2 = cv.inRange(img_hsv, lower2, upper2)
    img_mask3 = cv.inRange(img_hsv, lower3, upper3)
    img_mask = img_mask1 | img_mask2 | img_mask3

    kernel = np.ones((7, 7), np.uint8)
    img_mask = cv.morphologyEx(img_mask, cv.MORPH_OPEN, kernel)
    img_mask = cv.morphologyEx(img_mask, cv.MORPH_CLOSE, kernel)
    return img_mask


# R,B,Y 각 색깔을 카메라에 그리는 함수. color 의 경우 'red', 'blue', 'green(전방)' 존재

def drawing(camera, img_mask, color):
    number, _, stats, centroids = cv.connectedComponentsWithStats(img_mask)
    count = 0

    for idx, centroid in enumerate(centroids):
        if stats[idx][0] == 0 and stats[idx][1] == 0:
            continue
        if np.any(np.isnan(centroid)):
            continue

        x, y, wid, hei, area = stats[idx]
        cx, cy = int(centroid[0]), int(centroid[1])
        # print(area)
        # 작은 영역의 노이즈를 최소화 하기 위해 area 가 erase_noise_area 이상인 경우에 대해서만 검출
        if area > erase_noise_area:
            # print(area)
            if (color == 'red') | (color == 'blue'):  # 빨간색 영역 or 파란색 영역
                # 배경을 제외하고 검출된 색깔을 count 하여 number-1 과 비교
                for cen in centroids:
                    if cen[0] > int((width / 3) * 2):
                        count += 1
                    elif cen[0] < int(width / 3):
                        count -= 1
                if abs(count) == int(number) - 1:
                    # 한쪽에만 있는 경우
                    confirm = 0
                else:
                    # 양쪽에 있는 경우
                    confirm = 1

                # cv.circle(camera, (cx, cy), 10, (255, 255, 255), 10)
                if (cx < int(width / 2) & confirm == 0):
                    state = 'L'
                elif (cx > int(width / 2) & confirm == 0):
                    state = 'R'
                elif (confirm == 1):
                    state = 'M'
                else:
                    state = 'n'
                return state

            if color == 'green':  # 초록색 로봇
                cv.circle(camera, (cx, cy), 10, (0, 255, 0), 10)
                # cv.rectangle(camera, (x, y), (x + wid, y + hei), (0, 255, 0))

                # 로봇의 area 가 전체 넓이의 battle_mode_area 이상일 경우 battle mode 로 변경(실험을 통한 값 선정 요망)
                if area > battle_mode_area:
                    state = 'GO'
                    # print('battle mode')
                    # print(area)
                else:
                    if cx < int((width / 8) * 3):
                        state = 'l'
                    elif cx > int((width / 8) * 5):
                        state = 'r'
                    else:
                        state = 'm'
                return state

while True:
    try:
        _, front_Camera = main_cap.read()
        front_Camera = cv.resize(front_Camera, (width, height), interpolation=cv.INTER_AREA)
        img_hsv_front = cv.cvtColor(front_Camera, cv.COLOR_BGR2HSV)
        # mask 를 씌워 전방 카메라의 R,B,Y 이미지 반환 (이미지, hsv, threshold)

        # hsv 와 threshold 는 상황에 맞게 즉각 수정
        img_mask_red_front = masking(img_hsv_front, 2, 50)
        img_mask_blue_front = masking(img_hsv_front, 113, 85)
        img_mask_green_front = masking(img_hsv_front, 57, 30)

        # 색 인식에 따른 행동을 위한 state 값 정의
        Green_state = drawing(front_Camera, img_mask_green_front, 'green')

        # 로봇을 감지한 경우(area 가 battle mode area 이상), 배틀 모드로 바뀌어 Final_state 는 바닥색으로 반환
        if Green_state == 'l' or Green_state == 'r' or Green_state == 'm':
            Final_state = Green_state
        elif Green_state == 'GO':
            Red_state = drawing(front_Camera, img_mask_red_front, 'red')
            if Red_state == 'L' or Red_state == 'R' or Red_state == 'M':
                Final_state = Red_state
            else:
                Blue_state = drawing(front_Camera, img_mask_blue_front, 'blue')
                if Blue_state == 'L' or Blue_state == 'R' or Blue_state == 'M':
                    Final_state = Blue_state
                else:
                    Final_state = 'G'
        else:
            Final_state = 'n'
        # 로봇을 감지하지 못한 경우 'n' 전송
        # print(Final_state)

        if ser.writable:
            Trans_state = Final_state.encode('utf-8')
            ser.write(Trans_state)

        cv.imshow('front_Camera', front_Camera)
        # mask 영역이 정상적으로 생성되고 있는지에 대한 확인
        # if Green_state == 'GO':
        #    img_mask_front = img_mask_red_front | img_mask_green_front | img_mask_blue_front
        #    cv.imshow('mask', img_mask_front)
        # else:
        #    img_mask_front = img_mask_green_front

        if cv.waitKey(1) & 0xFF == 27:
            break
    except:
        if main_cap == cap0:
            cap0.release()
            cap1 = cv.VideoCapture('/dev/video1', cv.CAP_V4L2)
            main_cap = cap1
        elif main_cap == cap1:
            cap1.release()
            cap0 = cv.VideoCapture('/dev/video0', cv.CAP_V4L2)
            main_cap = cap0

cv.destroyAllWindows()