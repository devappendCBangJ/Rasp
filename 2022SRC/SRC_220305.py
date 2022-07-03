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

"""
# GPIO 번호 규칙 지정 + 핀 지정
GPIO.setmode(GPIO.BCM)      # GPIO 핀들의 번호를 지정하는 규칙 설정
servo_pin = 12                   # 서보핀은 라즈베리파이 GPIO 12번핀으로 
GPIO.setup(servo_pin, GPIO.OUT)  # 서보핀을 출력으로 설정 
servo = GPIO.PWM(servo_pin, 50)  # 서보핀을 PWM 모드 50Hz로 사용
servo.start(90)  # 서보모터의 초기값을 0으로 설정

servo_min_duty = 3               # 최소 듀티비를 3으로
servo_max_duty = 12              # 최대 듀티비를 12로

def servo_move(degree):    # 각도를 입력하면 듀티비를 알아서 설정해주는 함수
    # 각도는 최소0, 최대 180으로 설정
    if degree > 180:
        degree = 180
    elif degree < 0:
        degree = 0

    # 입력한 각도(degree)를 듀티비로 환산하는 식
    # servo.start(degree)
    duty = servo_min_duty+(degree*(servo_max_duty-servo_min_duty)/180.0)
    # 환산한 듀티비를 서보모터에 전달
    servo.ChangeDutyCycle(duty)
    # servo.stop()
"""

# 시리얼 설정
ser = serial.Serial(                # serial 객체
    port = '/dev/ttyAMA1',          # serial통신 포트
    baudrate = 115200,              # serial통신 속도
    parity = serial.PARITY_EVEN,    # 패리티 비트 설정
    stopbits = serial.STOPBITS_ONE, # 스톱 비트 설정
    bytesize = serial.EIGHTBITS,    # 데이터 비트수
    timeout = 1                     # 타임 아웃 설정
)

# 카메라 설정, 화면 사이즈, hsv
# cap = cv2.VideoCapture(cv2.CAP_DSHOW + 1)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
W_View_size = 320
H_View_size = 240
'''cap.set(3, W_View_size)
cap.set(4, H_View_size)'''

green_hue = 70
green_low_th = 60
green_up_th = 255

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
count=0
FPS=list()
ang = 90
while True:
    curTime = time.time()
    sec = curTime - prevTime
    fps = 1/sec
    FPS.append(fps)
    count=count+1
    if(count==50):
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
    temp = 0
    if stats[idx][0] != 0 or stats[idx][1] != 0:
        if(centervsX_R < W_View_size * 4 / 11):
            ras_res += "1"
            temp = 1
        elif(W_View_size * 4 / 11 <= centervsX_R <= W_View_size * 7 / 11):
            ras_res += "2"
            temp = 2
        elif(W_View_size * 7 / 11 < centervsX_R):
            ras_res += "3"
            temp = 3

        if(areavs < green_small):
            ras_res += ",0"
        elif(green_small <= areavs <= green_big):
            ras_res += ",1"
        elif(green_big < areavs):
            ras_res += ",2"
        
        # 시각화
        # print('fps : ', fps, '/centervsX_R : ', centervsX_R, '/ras_res : ', ras_res)
        # print('/fps : ', fps, '/areavs : ', areavs, '/centervsX_R : ', centervsX_R, '/centervsY_R : ', centervsY_R)
        cv2.circle(img_color, (centervsX_R, centervsY_R), 10, (0, 0, 255), 10)
    else:
        ras_res += "9,9"

    ras_res += ",9/"
    
    if(temp == 1):
        # ang -= 3
        pass
    elif(temp == 2):
        # ang = ang
        pass
    elif(temp == 3):
        # ang += 3
        pass
    # servo_move(ang)
    # print("ang : ", ang)


    # 시리얼 쓰기
    #for i in range(len(ras_res)):
        # print(ras_res[i])
        # ser.write(ras_res[i].encode())
        # time.sleep(0.005)
    # 시리얼 쓰기
    ser.write(ras_res.encode())
    # 시리얼 읽기
    '''if ser.readable():
        res = ser.readline()
        print(res.decode()[:len(res) - 1])'''

    # 시각화
    cv2.imshow('img_color', img_color)
    cv2.imshow('img_mask', img_mask)
    #cv2.imshow('img_result', img_result)

    # 카메라 종료 조건
    if cv2.waitKey(1) & 0xFF == 27:
        break
    prevTime = curTime

cap.release()
cv2.destoryAllWindows()

GPIO.cleanup()                      # GPIO 핀들을 초기화