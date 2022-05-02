import time
import serial
import cv2
import numpy as np
import RPi.GPIO as GPIO

# GPIO 번호 규칙 지정 + 핀 지정
GPIO.setmode(GPIO.BCM)      # GPIO 핀들의 번호를 지정하는 규칙 설정
servo_pin = 12                   # 서보핀은 라즈베리파이 GPIO 12번핀으로 
GPIO.setwarnings(False)
GPIO.setup(servo_pin, GPIO.OUT)
servo = GPIO.PWM(servo_pin, 50)  # 서보핀을 PWM 모드 50Hz로 사용
servo.start(0)  # 서보모터의 초기값을 0으로 설정

servo_min_duty = 3.15               # 최소 듀티비를 3으로
servo_max_duty = 11.4              # 최대 듀티비를 12로
'''
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
lower_green = (50,45,62)
upper_green = (75,239,216)
#blue
lower_blue = (109, 97, 82)
upper_blue = (117, 255, 155)
#red


# 원통 크기 기준, 통신 데이터 리스트
green_small = W_View_size * H_View_size * 0.0005
green_middle = W_View_size * H_View_size * 0.0025
green_big = W_View_size * H_View_size * 0.005834
ras_res= ""

time1=0
time2=0

flag = True
count = 0

if not cap.isOpened():
    print('ERROR! Unable to open camara')
    
'''
cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
'''

kernel = np.ones((5, 5), np.uint8)

def Masking(img_hsv,lower,upper):
    
    img_mask = cv2.inRange(img_hsv, lower, upper)
    #모폴로지
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_OPEN, kernel)
    img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_CLOSE, kernel)
    return img_mask


ang = 90
Check_fps = list()
while True:
    
    
    time1=time.time()
    # 카메라 읽기
    ret,frame = cap.read()
    frame = cv2.resize(frame, dsize=(W_View_size, H_View_size), interpolation=cv2.INTER_AREA)
    if not ret:
        continue

    # hsv 변환, 노이즈제거, 마스크형성
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    bin_image = Masking(img_hsv,lower_green,upper_green)

    #컨투어
    contours, _ = cv2.findContours(bin_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    max_contour = None
    max_area = -1

    for contour in contours: # 컨투어 제일 넓이 큰거 하나만 구하는 과정
        area = cv2.contourArea(contour)
        print(area)
        if cv2.contourArea(contour) < 40:  #  너무 작으면 무시(노이즈제거)
            continue
        if area>max_area:
            max_area = area
            max_contour = contour

    x, y, w, h = cv2.boundingRect(max_contour)

    centerX, centerY = x+w/2, y+h/2

    cv2.rectangle(bin_image, (x, y), (x+w, y+h), (255, 0, 0), 2)


    # 결과 연산, 시리얼 통신
    ras_res = ""
    if(len(contours) != 0): #contours 존재하면
        if(max_area < green_small):
            if(centerX < W_View_size * 3.5 / 11):
                ras_res += "1,1"
            elif(W_View_size * 3.5 / 11 <= centerX <= W_View_size * 7.5 / 11):
                ras_res += "2,1"
            elif(W_View_size * 7.5 / 11 < centerX):
                ras_res += "3,1"
        elif(green_small <= max_area <= green_middle):
            if(centerX < W_View_size * 3 / 11):
                ras_res += "1,2"
            elif(W_View_size * 3 / 11 <= centerX <= W_View_size * 8 / 11):
                ras_res += "2,2"
            elif(W_View_size * 8 / 11 < centerX):
                ras_res += "3,2"
        elif(green_middle <= max_area <= green_big):
            if(centerX < W_View_size * 2.5 / 11):
                ras_res += "1,3"
            elif(W_View_size * 2.5 / 11 <= centerX <= W_View_size * 8.5 / 11):
                ras_res += "2,3"
            elif(W_View_size * 8.5 / 11 < centerX):
                ras_res += "3,3"
        elif(green_big < max_area):
            if(centerX < W_View_size * 3 / 11):
                ras_res += "1,4"
            elif(W_View_size * 3 / 11 <= centerX <= W_View_size * 8 / 11):
                ras_res += "2,4"
            elif(W_View_size * 8 / 11 < centerX):
                ras_res += "3,4"
            print(ras_res)
    #elif((centerX!=0 and centerY!=0) and (len(contours) ==0)): 여기서 좀 더 세부적으로 나눌거임.
        #ras_res += "9,9"
    else: #contours 없으면
        ras_res += "9,9"
        print(ras_res)
    ras_res += ",9/"
    
    #servo_move(ang)

    ser.write(ras_res.encode())


    cv2.imshow('frame', frame)
    
    cv2.imshow('dst', bin_image)
    time2 = time.time()
    
    sec = time2-time1
    fps = 1/sec
    
    Check_fps.append(fps)

    average=np.mean(Check_fps)

    print(f"평균FPS : {average}")
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

GPIO.cleanup()