# pip install pyserial

# 1. 시리얼 설정
    # - 반드시 전압레벨이 같게 맞춘 상태로 통신

    # port : 라즈베리파이 시리얼포트(UART) 경로 설정
    # baudrate : 통신 속도 설정
        # - 라즈베리파이-아두이노 같게 설정
    # parity : 통신 오류검사 비트 설정
        # - 기본값 : 패리티 검사x
        # - 라즈베리파이-아두이노 같게 설정
    # stopbits : 데이터 끝을 알리기 위한 비트 설정
        # - 기본값 : 1비트의 stopbits
    # bytesize : 데이터 비트 총 숫자 설정
        # - 일반값 : 8비트의 bitsize
    # timeout : 시리얼 명령어가 시리얼 통신 종료까지 기다리는 시간

# 모듈 불러오기
import time
import serial
import cv2
import numpy as np
import RPi.GPIO as GPIO

import math

# 시리얼 설정
ser = serial.Serial(                # serial 객체
    port = '/dev/ttyACM0',          # serial통신 포트
    baudrate = 9600,              # serial통신 속도
    timeout = 1                     # 타임 아웃 설정
)

# 카메라 설정, 화면 사이즈, hsv
# cap = cv2.VideoCapture(cv2.CAP_DSHOW + 1)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
W_View_size = 320
H_View_size = 240
'''cap.set(3, W_View_size)
cap.set(4, H_View_size)'''

# green
green_hue = 65
green_low_th = 90
green_up_th = 255

#blue
blue_hue = 117
blue_low_th = 100
blue_up_th = 255

#red
red_hue = 180
red_low_th = 110
red_up_th = 255

#yellow
yellow_hue = 15
yellow_low_th = 100
yellow_up_th = 255

# 원통 크기 기준, 통신 데이터 리스트
green_small = W_View_size * H_View_size * 0.005
green_big = W_View_size * H_View_size * 0.01
ras_res= ""

# 타이머
curTime = 0
prevTime = 0
count=0
FPS=list()

# 통신 초기값
turn = '99'
ang = 99

# 모드 초기값
mode = 1

# mask 형성, 노이즈 제거, 마스크 리턴
def masking(img_hsv, hue, low_th, up_th):
    if hue < 10:
        lower1 = np.array([hue - 10 + 180, low_th, low_th])
        upper1 = np.array([180, up_th, up_th])
        lower2 = np.array([0, low_th, low_th])
        upper2 = np.array([hue, up_th, up_th])
        lower3 = np.array([hue, low_th, low_th])
        upper3 = np.array([hue + 10, up_th, up_th])
    elif hue > 170:
        lower1 = np.array([hue, low_th, low_th])
        upper1 = np.array([180, up_th, up_th])
        lower2 = np.array([0, low_th, low_th])
        upper2 = np.array([hue + 10 - 180, up_th, up_th])
        lower3 = np.array([hue - 10, low_th, low_th])
        upper3 = np.array([hue, up_th, up_th])
    else:
        lower1 = np.array([hue, low_th, low_th])
        upper1 = np.array([hue + 10, up_th, up_th])
        lower2 = np.array([hue - 10, low_th, low_th])
        upper2 = np.array([hue, up_th, up_th])
        lower3 = np.array([hue - 10, low_th, low_th])
        upper3 = np.array([hue, up_th, up_th])

    img_mask1 = cv2.inRange(img_hsv, lower1, upper1)
    img_mask2 = cv2.inRange(img_hsv, lower2, upper2)
    img_mask3 = cv2.inRange(img_hsv, lower3, upper3)
    img_mask = img_mask1 | img_mask2 | img_mask3

    kernel = np.ones((5, 5), np.uint8)
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_OPEN, kernel)
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_CLOSE, kernel)
    return img_mask

while True:
    # fps 측정
    curTime = time.time()
    sec = curTime - prevTime
    fps = 1/sec
    FPS.append(fps)
    count=count+1
    if(count==20):
        print(np.mean(FPS))
        FPS=[]
        count=0
    # 카메라 읽기
    ret,img_color = cap.read()
    img_color = cv2.resize(img_color, dsize=(W_View_size, H_View_size), interpolation=cv2.INTER_AREA)
    if not ret:
        continue

    # hsv 변환, 마스크 형성, 노이즈 제거, 특징 추출
    img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
    img_mask_g = masking(img_hsv, green_hue, green_low_th, green_up_th)
    img_result_g = cv2.bitwise_and(img_color, img_color, mask=img_mask_g)
    numOfLabels_g, img_label_g, stats_g, centroids_g = cv2.connectedComponentsWithStats(img_mask_g)
    
    img_mask_r = masking(img_hsv, red_hue, red_low_th, red_up_th)
    img_result_r = cv2.bitwise_and(img_color, img_color, mask=img_mask_r)
    numOfLabels_r, img_label_r, stats_r, centroids_r = cv2.connectedComponentsWithStats(img_mask_r)
    
    img_mask_b = masking(img_hsv, blue_hue, blue_low_th, blue_up_th)
    img_result_b = cv2.bitwise_and(img_color, img_color, mask=img_mask_b)
    numOfLabels_b, img_label_b, stats_b, centroids_b = cv2.connectedComponentsWithStats(img_mask_b)
    
    img_mask_y = masking(img_hsv, yellow_hue, yellow_low_th, yellow_up_th)
    img_result_b = cv2.bitwise_and(img_color, img_color, mask=img_mask_y)
    numOfLabels_y, img_label_y, stats_y, centroids_y = cv2.connectedComponentsWithStats(img_mask_y)
    
    # 특징 전처리 - green
    areavs_g = 0 # while문 돌때마다 초기화
    centervsX_R_g = 0
    centervsY_R_g = 0
    for idx_g, centroid_g in enumerate(centroids_g):
        if stats_g[idx_g][0] == 0 and stats_g[idx_g][1] == 0:
            continue
        if np.any(np.isnan(centroid_g)):
            continue
        x_g, y_g, width_g, height_g, area_g = stats_g[idx_g]

        centerX_g, centerY_g = int(centroid_g[0]), int(centroid_g[1])
        if area_g > areavs_g:
            xvs_g = x_g
            widthvs_g = width_g
            areavs_g = area_g
            centervsX_R_g = centerX_g
            centervsY_R_g = centerY_g
    if areavs_g > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
        cv2.circle(img_color, (centervsX_R_g, centervsY_R_g), 10, (0, 255, 0), 10)

    # 특징 전처리 - red
    areavs_r = 0 # while문 돌때마다 초기화
    centervsX_R_r = 0
    centervsY_R_r = 0
    for idx_r, centroid_r in enumerate(centroids_r):
        if stats_r[idx_r][0] == 0 and stats_r[idx_r][1] == 0:
            continue
        if np.any(np.isnan(centroid_r)):
            continue
        x_r, y_r, width_r, height_r, area_r = stats_r[idx_r]

        centerX_r, centerY_r = int(centroid_r[0]), int(centroid_r[1])
        if area_r > areavs_r:
            xvs_r = x_r
            widthvs_r = width_r
            areavs_r = area_r
            centervsX_R_r = centerX_r
            centervsY_R_r = centerY_r
    if areavs_r > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
        cv2.circle(img_color, (centervsX_R_r, centervsY_R_r), 10, (0, 0, 255), 10)

    # 특징 전처리 - blue
    areavs_b = 0 # while문 돌때마다 초기화
    centervsX_R_b = 0
    centervsY_R_b = 0
    for idx_b, centroid_b in enumerate(centroids_b):
        if stats_b[idx_b][0] == 0 and stats_b[idx_b][1] == 0:
            continue
        if np.any(np.isnan(centroid_b)):
            continue
        x_b, y_b, width_b, height_b, area_b = stats_b[idx_b]

        centerX_b, centerY_b = int(centroid_b[0]), int(centroid_b[1])
        if area_b > areavs_b:
            xvs_b = x_b
            widthvs_b = width_b
            areavs_b = area_b
            centervsX_R_b = centerX_b
            centervsY_R_b = centerY_b
    if areavs_b > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
        cv2.circle(img_color, (centervsX_R_b, centervsY_R_b), 10, (255, 0, 0), 10)
    
    # 특징 전처리 - yellow
    areavs_y = 0 # while문 돌때마다 초기화
    centervsX_R_y = 0
    centervsY_R_y = 0
    for idx_y, centroid_y in enumerate(centroids_y):
        if stats_y[idx_y][0] == 0 and stats_y[idx_y][1] == 0:
            continue
        if np.any(np.isnan(centroid_y)):
            continue
        x_y, y_y, width_y, height_y, area_y = stats_y[idx_y]

        centerX_y, centerY_y = int(centroid_y[0]), int(centroid_y[1])
        if area_y > areavs_y:
            xvs_y = x_y
            widthvs_y = width_y
            areavs_y = area_y
            centervsX_R_y = centerX_y
            centervsY_R_y = centerY_y
    if areavs_y > 80:  # 크기가 80 이상이면 동그라미, 사각형인정
        cv2.circle(img_color, (centervsX_R_y, centervsY_R_y), 10, (0, 255, 255), 10)
    
    # main 움직임 판단
    if(mode == 1):
        # 목적지까지의 각도 계산
        if ('centervsX_R_b' in globals()) and ('centervsY_R_b' in globals()) and ('centervsX_R_r' in globals()) and ('centervsY_R_r' in globals()) and ('centervsY_R_g' in globals()) and ('centervsY_R_g' in globals()):
            cv2.line(img_color, (centervsX_R_b,centervsY_R_b), (centervsX_R_r,centervsY_R_r), (255,255,255), 3)
            cv2.line(img_color, (centervsX_R_b,centervsY_R_b), (centervsX_R_g,centervsY_R_g), (255,255,255), 3)
            rad_br = math.atan2(centervsX_R_b - centervsX_R_r, centervsY_R_b - centervsY_R_r)
            rad_bg = math.atan2(centervsX_R_b - centervsX_R_g, centervsY_R_b - centervsY_R_g)
            PI = math.pi
            deg_br = (rad_br*180)/PI
            deg_bg = (rad_bg*180)/PI
            if(deg_br < 0):
                deg_br = 360 - abs(deg_br)
            if(deg_bg < 0):
                deg_bg = 360 - abs(deg_bg)
                
            if(deg_br <= deg_bg):
                if((deg_bg - deg_br) < 180):
                    ang = deg_bg - deg_br
                    turn = '0' # left turn
                else:
                    ang = deg_br -(deg_bg - 360)
                    turn = '2' # right turn
            elif(deg_bg < deg_br): # bg, br
                if((deg_br - deg_bg) < 180):
                    ang = deg_br - deg_bg
                    turn = '2' # right turn
                else:
                    ang = deg_bg -(deg_br - 360)
                    turn = '0' # left turn
            
            # 중심점 사이 거리
            center_len = ((centervsX_R_r-centervsX_R_g)**2 + (centervsY_R_r-centervsY_R_g)**2)**(1/2)
            print("물체 사이 거리 : ", center_len)
            if(center_len <= 80 and ang <= 20):
                turn = '3'
                mode = 2
            elif(center_len > 80 and ang <= 20):
                turn = '1'
                
    if(mode == 2):
        # 목적지까지의 각도 계산
        if ('centervsX_R_b' in globals()) and ('centervsY_R_b' in globals()) and ('centervsX_R_r' in globals()) and ('centervsY_R_r' in globals()) and ('centervsY_R_y' in globals()) and ('centervsY_R_y' in globals()):
            cv2.line(img_color, (centervsX_R_b,centervsY_R_b), (centervsX_R_r,centervsY_R_r), (255,255,255), 3)
            cv2.line(img_color, (centervsX_R_b,centervsY_R_b), (centervsX_R_y,centervsY_R_y), (255,255,255), 3)
            rad_br = math.atan2(centervsX_R_b - centervsX_R_r, centervsY_R_b - centervsY_R_r)
            rad_by = math.atan2(centervsX_R_b - centervsX_R_y, centervsY_R_b - centervsY_R_y)
            PI = math.pi
            deg_br = (rad_br*180)/PI
            deg_by = (rad_by*180)/PI
            if(deg_br < 0):
                deg_br = 360 - abs(deg_br)
            if(deg_by < 0):
                deg_by = 360 - abs(deg_by)
                
            if(deg_br <= deg_by):
                if((deg_by - deg_br) < 180):
                    ang = deg_by - deg_br
                    turn = '0' # left turn
                else:
                    ang = deg_br -(deg_by - 360)
                    turn = '2' # right turn
            elif(deg_by < deg_br): # bg, br
                if((deg_br - deg_by) < 180):
                    ang = deg_br - deg_by
                    turn = '2' # right turn
                    time.sleep(2)
                else:
                    ang = deg_by -(deg_br - 360)
                    turn = '0' # left turn
            
            # 중심점 사이 거리
            center_len = ((centervsX_R_r-centervsX_R_y)**2 + (centervsY_R_r-centervsY_R_y)**2)**(1/2)
            print("물체 사이 거리 : ", center_len)
            if(center_len <= 30 and ang <= 20):
                turn = '3'
                mode = 1
            elif(center_len > 30 and ang <= 20):
                turn = '1'
        
        # # 확인용 코드
        # print("deg_br :", deg_br)
        # print("deg_bg :", deg_bg)
        # print("turn :", turn)
        # print("ang :", ang)
        
    # 결과 연산, 시리얼 통신
    ras_res = ""
    temp = 0
    
    ras_res += str(int(ang))
    ras_res += ','
    ras_res += str(turn)
    print("통신값(방향, 각도) : ", ras_res) # 확인용 코드
    ser.write(ras_res.encode())
        
        # 시각화
        # print('fps : ', fps, '/centervsX_R : ', centervsX_R, '/ras_res : ', ras_res)
        # print('/fps : ', fps, '/areavs : ', areavs, '/centervsX_R : ', centervsX_R, '/centervsY_R : ', centervsY_R)

    # 시각화
    cv2.imshow('img_color', img_color)
    cv2.imshow('img_mask_g', img_mask_g)
    cv2.imshow('img_mask_r', img_mask_r)
    cv2.imshow('img_mask_b', img_mask_b)
    cv2.imshow('img_mask_y', img_mask_y)
    #cv2.imshow('img_result', img_result)

    # 카메라 종료 조건
    if cv2.waitKey(1) & 0xFF == 27:
        break
    prevTime = curTime

cap.release()
cv2.destoryAllWindows()

GPIO.cleanup()                      # GPIO 핀들을 초기화