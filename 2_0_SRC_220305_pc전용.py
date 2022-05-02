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
# import serial
import cv2
import numpy as np

# # 시리얼 설정
# ser = serial.Serial(                # serial 객체
#     port = '/dev/ttyAMA1',          # serial통신 포트
#     baudrate = 115200,              # serial통신 속도
#     parity = serial.PARITY_NONE,    # 패리티 비트 설정
#     stopbits = serial.STOPBITS_ONE, # 스톱 비트 설정
#     bytesize = serial.EIGHTBITS,    # 데이터 비트수
#     timeout = 1                     # 타임 아웃 설정
# )

# 카메라 설정, 화면 사이즈, hsv
cap = cv2.VideoCapture(cv2.CAP_DSHOW + 1)
# cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
W_View_size = 640
H_View_size = 360
cap.set(3, W_View_size)
cap.set(4, H_View_size)

green_hue = 110
green_low_th = 55
green_up_th = 210

# 원통 크기 기준, 통신 데이터 리스트
green_small = W_View_size * H_View_size * 0.005
green_big = W_View_size * H_View_size * 0.01
ras_res= ""

# 타이머
curTime = 0
prevTime = 0

# mask 형성, 노이즈 제거, 마스크 리턴
def masking(img_hsv, hue, low_th, up_th):
    if hue < 10:
        lower1 = np.array([hue - 10 + 180, low_th, low_th])
        upper1 = np.array([180, up_th_th, up_th])
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
    curTime = time.time()
    sec = curTime - prevTime
    fps = 1/sec

    # 카메라 읽기
    ret,img_color = cap.read()
    if not ret:
        continue

    # hsv 변환, 마스크 형성, 노이즈 제거, 특징 추출
    img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
    img_mask = masking(img_hsv, green_hue, green_low_th, green_up_th)
    img_result = cv2.bitwise_and(img_color, img_color, mask=img_mask)
    numOfLabels, img_label, stats, centroids = cv2.connectedComponentsWithStats(img_mask)
    
    # 특징 전처리
    areavs = 0 # while문 돌때마다 초기화
    for idx, centroid in enumerate(centroids):
        if stats[idx][0] == 0 and stats[idx][1] == 0:
            continue
        if np.any(np.isnan(centroid)):
            continue
        x, y, width, height, area = stats[idx]

        centerX, centerY = int(centroid[0]), int(centroid[1])
        if area > areavs:
            xvs = x
            widthvs = width
            areavs = area
            centervsX_R = centerX
            centervsY_R = centerY
    
    # 결과 연산, 시리얼 통신
    ras_res = ""
    if stats[idx][0] != 0 or stats[idx][1] != 0:
        if(centervsX_R < 250):
            ras_res += "1"
        elif(250 <= centervsX_R <= 350):
            ras_res += "2"
        elif(350 < centervsX_R):
            ras_res += "3"
        else:
            ras_res += "0"

        if(areavs < green_small):
            ras_res += ",0"
        elif(green_small <= areavs <= green_big):
            ras_res += ",1"
        elif(green_big < areavs):
            ras_res += ",2"

        ras_res += ",0/"

        print('/centervsX_R : ', centervsX_R, '/ras_res : ', ras_res)
        # print('/fps : ', fps, '/areavs : ', areavs, '/centervsX_R : ', centervsX_R, '/centervsY_R : ', centervsY_R)
        cv2.circle(img_color, (centervsX_R, centervsY_R), 10, (0, 0, 255), 10)
        prevTime = curTime

        # # 시리얼 통신
        # for i in range(len(ras_res)):
        #     # print(ras_res[i])
        #     ser.write(ras_res[i].encode())
        #     # time.sleep(0.005)

    # 시각화
    cv2.imshow('img_color', img_color)
    cv2.imshow('img_mask', img_mask)
    cv2.imshow('img_result', img_result)

    # 카메라 종료 조건
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destoryAllWindows()