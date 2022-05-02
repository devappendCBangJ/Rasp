#
#      공대선배 라즈베리파이썬 #10 스위치로 서보모터 제어
#      youtube 바로가기: https://www.youtube.com/c/공대선배
#      스위치를 이용해 서보모터를 제어하는 코드
#

import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
from time import sleep      #time 라이브러리의 sleep함수 사용

GPIO.setmode(GPIO.BCM)      # GPIO 핀들의 번호를 지정하는 규칙 설정

### 이부분은 아두이노 코딩의 setup()에 해당합니다
servo_pin = 12                   # 서보핀은 라즈베리파이 GPIO 12번핀으로 
sw1_pin = 16                     # 스위치1 핀은 라즈베리파이 GPIO 16번핀으로
sw2_pin = 20                     # 스위치2 핀은 라즈베리파이 GPIO 20번핀으로

GPIO.setup(servo_pin, GPIO.OUT)  # 서보핀을 출력으로 설정 
# 스위치1, 2 핀을 풀다운저항이 있는 입력으로 설정
GPIO.setup(sw1_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)   
GPIO.setup(sw2_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)   

servo = GPIO.PWM(servo_pin, 50)  # 서보핀을 PWM 모드 50Hz로 사용
servo.start(0)  # 서보모터의 초기값을 0으로 설정

servo_deg = 0   # 서보모터의 현재 각도 설정
servo_min_duty = 3               # 최소 듀티비를 3으로
servo_max_duty = 12              # 최대 듀티비를 12로

def set_servo_degree(degree):    # 각도를 입력하면 듀티비를 알아서 설정해주는 함수
    # 각도는 최소0, 최대 180으로 설정
    if degree > 180:
        degree = 180
    elif degree < 0:
        degree = 0

    # 입력한 각도(degree)를 듀티비로 환산하는 식
    duty = servo_min_duty+(degree*(servo_max_duty-servo_min_duty)/180.0)
    # 환산한 듀티비를 서보모터에 전달
    servo.ChangeDutyCycle(duty)

### 이부분은 아두이노 코딩의 loop()에 해당합니다
try:                                    # 이 try 안의 구문을 먼저 수행하고
    while True:                         # 무한루프 시작: 아두이노의 loop()와 같음
        if GPIO.input(sw1_pin) == GPIO.HIGH:     # 스위치1 핀이 HIGH이면  
            servo_deg += 10                      # 서보모터 각도를 10도 증가
            set_servo_degree(servo_deg)          # 증가된 각도만큼 서보모터 움직임
            print(servo_deg)                     # 현재 각도를 화면에 출력
            sleep(1)                             # 1초간 대기
        elif GPIO.input(sw2_pin) == GPIO.HIGH:   # 스위치2 핀이 HIGH이면
            servo_deg -= 10
            set_servo_degree(servo_deg)
            print(servo_deg)
            sleep(1)
        
        if servo_deg > 170:
            servo_deg = 170
        elif servo_deg < 10:
            servo_deg = 10

### 이부분은 반드시 추가해주셔야 합니다.
finally:                                # try 구문이 종료되면
    GPIO.cleanup()                      # GPIO 핀들을 초기화
