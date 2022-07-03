import time
import serial
import cv2
import numpy as np
import RPi.GPIO as GPIO
from collections import deque

# GPIO 번호 규칙 지정 + 핀 지정
'''
GPIO.setmode(GPIO.BCM)      # GPIO 핀들의 번호를 지정하는 규칙 설정
servo_pin = 12                   # 서보핀은 라즈베리파이 GPIO 12번핀으로 
GPIO.setwarnings(False)
GPIO.setup(servo_pin, GPIO.OUT)
servo = GPIO.PWM(servo_pin, 50)  # 서보핀을 PWM 모드 50Hz로 사용
servo.start(0)  # 서보모터의 초기값을 0으로 설정

servo_min_duty = 3.15               # 최소 듀티비를 3으로
servo_max_duty = 11.4              # 최대 듀티비를 12로

def servo_move(degree):    # 각도를 입력하면 듀티비를 알아서 설정해주는 함수
    # 각도는 최소0, 최대 180으로 설정
    if degree > 180:
        degree = 180
    elif degree < 0:
        degree = 0

    # 입력한 각도(degree)를 듀티비로 환산하는 식
    duty = servo_min_duty+(degree*(servo_max_duty-servo_min_duty)/180.0)
    # 환산한 듀티비를 서보모터에 전달
    GPIO.setup(servo_pin, GPIO.OUT)  # ★서보핀을 출력으로 설정
    servo.ChangeDutyCycle(duty)                    # ★0.3초 쉼
    GPIO.setup(servo_pin, GPIO.IN)  # ★서보핀을 입력으로 설정 (더이상 움직이지 않음)
'''
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
W_View_size = 400
H_View_size = 300
'''cap.set(3, W_View_size)
cap.set(4, H_View_size)'''


#green
#lower_green = (50,45,62)
#upper_green = (75,239,216)

lower_green = (54,80,75)
upper_green = (75,255,255)
#blue
lower_blue = (102, 150, 90)
upper_blue = (110, 255, 200)
#red
lower_red = (171, 120, 160)
upper_red = (178, 230, 255)

# 원통 크기 기준, 통신 데이터 리스트
green_small = W_View_size * H_View_size * 0.0005
green_middle = W_View_size * H_View_size * 0.0025
green_big = W_View_size * H_View_size * 0.005834
ras_res= ""


FPS=list()
if not cap.isOpened():
    print('ERROR! Unable to open camara')
    
'''
cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
'''

kernel = np.ones((5, 5), np.uint8)

rx,rw =0,0
    
def Masking(img_hsv,lower,upper):
    
    img_mask = cv2.inRange(img_hsv, lower, upper)
    #모폴로지
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_OPEN, kernel)
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_CLOSE, kernel)
    return img_mask

def get_contour(contours):
    max_contour = None
    max_area = -1
    for contour in contours: # 컨투어 제일 넓이 큰거 하나만 구하는 과정
        area = cv2.contourArea(contour)
        #print(area)
        if cv2.contourArea(contour) < 40:  #  너무 작으면 무시(노이즈제거)
            continue
        if area>max_area:
            max_area = area
            max_contour = contour
    return max_area,max_contour

def get_contour_red(contours):
    max_contour = None
    second_contour = None
    max_area = -1
    second_area = -1
    for contour in contours: # 컨투어 제일 넓이 큰거 하나만 구하는 과정
        area = cv2.contourArea(contour)
        #print(area)
        if cv2.contourArea(contour) < 100:  #  너무 작으면 무시(노이즈제거)
            continue
        if area>max_area:
            if max_area<area:
                max_area = area
                max_contour = contour
        elif max_area>area and area>second_area:
            second_area = area
            second_contour = contour
    return max_area,max_contour, second_area,second_contour

#ang = 90

count = 0
while True:
    
    start = time.perf_counter()
    '''
    curTime = time.time()
    sec = curTime - prevTime
    fps = 1/sec
    FPS.append(fps)
    count=count+1
    if(count==50):
        print("평균 fps:",np.mean(FPS))
        FPS=[]
        count=0
        '''
    # 카메라 읽기
    ret,frame = cap.read()
    frame = cv2.resize(frame, dsize=(W_View_size, H_View_size), interpolation=cv2.INTER_AREA)
    if not ret:
        continue
    # hsv 변환, 노이즈제거, 마스크형성
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    bin_image1 = Masking(img_hsv,lower_green,upper_green)
    bin_image2 = Masking(img_hsv,lower_blue,upper_blue)
    bin_image3 = Masking(img_hsv,lower_red,upper_red)
    bin_image4 = bin_image1|bin_image2|bin_image3

    #컨투어
    contours_green, _ = cv2.findContours(bin_image1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours_red, _ = cv2.findContours(bin_image3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours_blue, _ = cv2.findContours(bin_image2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    
    #컨투어 영역 제일 넓은 부분만 구하기(빨간색은 2번쨰까지)
    max_areaG, max_contourG = get_contour(contours_green)
    max_areaR, max_contourR, second_areaR, second_contourR = get_contour_red(contours_red)
    max_areaB, max_contourB = get_contour(contours_blue)
    gx, gy, gw, gh = cv2.boundingRect(max_contourG)
    rx1, ry1, rw1, rh1 = cv2.boundingRect(max_contourR)
    rx2, ry2, rw2, rh2 = cv2.boundingRect(second_contourR)

    if second_areaR == -1:
        rx = rx1
        rw = rw1
    else:
        if rx1 > rx2:
            rx = rx2
            rw = rx1+rw1-rx2
        else:
            rx = rx1
            rw = rw2+rx2-rx1
    
    bx, by, bw, bh = cv2.boundingRect(max_contourB)
    centerX, centerY = gx+gw/2, gy+gh/2
    #print("green: ",max_areaG)
    #print("red: ",max_areaR)
    cv2.rectangle(bin_image4, (gx, gy), (gx+gw, gy+gh), (255, 0, 0), 2)
    cv2.rectangle(bin_image4, (rx1, ry1), (rx1+rw1, ry1+rh1), (255, 0, 0), 2)
    cv2.rectangle(bin_image4, (rx2, ry2), (rx2+rw2, ry2+rh2), (255, 0, 0), 2)
    cv2.rectangle(bin_image4, (bx, by), (bx+bw, by+bh), (255, 0, 0), 2)
    
    
    #원영역 안에 원통 중심좌표 있을 경우
    inside = False
    
    if gx > rx and gx < rx+rw:
        inside = True
    
    # 결과 연산, 시리얼 통신
    ras_res = ""
    if(len(contours_green) != 0): #contours 존재하면
        if(max_areaG < green_small):
            if(centerX < W_View_size * 4 / 11):
                ras_res += "1,1"
            elif(W_View_size * 4 / 11 <= centerX <= W_View_size * 7 / 11):
                ras_res += "2,1"
            elif(W_View_size * 7 / 11 < centerX):
                ras_res += "3,1"
        elif(green_small <= max_areaG <= green_middle):
            if(centerX < W_View_size * 4 / 11):
                ras_res += "1,2"
            elif(W_View_size * 4 / 11 <= centerX <= W_View_size * 7 / 11):
                ras_res += "2,2"
            elif(W_View_size * 7 / 11 < centerX):
                ras_res += "3,2"
        elif(green_middle <= max_areaG <= green_big):
            if(centerX < W_View_size * 4 / 11):
                ras_res += "1,3"
            elif(W_View_size * 4 / 11 <= centerX <= W_View_size * 7 / 11):
                ras_res += "2,3"
            elif(W_View_size * 7 / 11 < centerX):
                ras_res += "3,3"
        elif(green_big < max_areaG):
            if(centerX < W_View_size * 4 / 11):
                ras_res += "1,4"
            elif(W_View_size * 4 / 11 <= centerX <= W_View_size * 7 / 11):
                ras_res += "2,4"
            elif(W_View_size * 7 / 11 < centerX):
                ras_res += "3,4"
            #print(ras_res)
    #elif((centerX!=0 and centerY!=0) and (len(contours) ==0)): 여기서 좀 더 세부적으로 나눌거임.
        #ras_res += "9,9"
    else: #contours 없으면
        ras_res += "9,9"
        #print(ras_res)
    
    #원통이 빨간 원 안에 있으면 마지막 자리 0, 아니면 1
    if inside:
        ras_res += ",0/"
    else:
        ras_res += ",1/"
    
    
        
    #servo_move(ang)

    ser.write(ras_res.encode())


    #cv2.imshow('frame', frame)
    cv2.imshow('dst', bin_image4)
    
    
    if cv2.waitKey(1) & 0xFF == 27:
        break
    end = time.perf_counter()
    sec = end-start
    fps = 1/sec
    FPS.append(fps)
    count=count+1
    if(count==20):
        print("평균 fps:", np.mean(FPS))
        # print("최소 fps:", np.min(FPS))
        FPS=[]
        count=0
    #prevTime = curTime    

cap.release()
cv2.destroyAllWindows()

#GPIO.cleanup()