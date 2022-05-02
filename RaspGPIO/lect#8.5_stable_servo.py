#
#      공대선배 라즈베리파이썬 #8.5 떨림없는 서보모터 제어
#      youtube 바로가기: https://www.youtube.com/c/공대선배
#      서보모터가 떨리지 않게 방지하며 제어하기
#

import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
from time import sleep      #time 라이브러리의 sleep함수 사용

GPIO.setmode(GPIO.BCM)      # GPIO 핀들의 번호를 지정하는 규칙 설정

### 이부분은 아두이노 코딩의 setup()에 해당합니다
servo_pin = 12                   # 서보핀은 라즈베리파이 GPIO 12번핀으로 

GPIO.setup(servo_pin, GPIO.OUT)  # 서보핀을 출력으로 설정 
servo = GPIO.PWM(servo_pin, 50)  # 서보핀을 PWM 모드 50Hz로 사용
servo.start(0)  # 서보모터의 초기값을 0으로 설정

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
    GPIO.setup(servo_pin, GPIO.OUT)  # ★서보핀을 출력으로 설정 
    servo.ChangeDutyCycle(duty)
    sleep(0.3)                        # ★0.3초 쉼
    GPIO.setup(servo_pin, GPIO.IN)  # ★서보핀을 입력으로 설정 (더이상 움직이지 않음)

### 이부분은 아두이노 코딩의 loop()에 해당합니다
try:                                    # 이 try 안의 구문을 먼저 수행하고
    while True:                         # 무한루프 시작: 아두이노의 loop()와 같음
        set_servo_degree(0)             # 서보모터의 각도를 0도로
        sleep(2)                        # 2초간 대기
        set_servo_degree(90)
        sleep(2)
        set_servo_degree(180)
        sleep(2)
        set_servo_degree(90)
        sleep(2)

### 이부분은 반드시 추가해주셔야 합니다.
finally:                                # try 구문이 종료되면
    GPIO.cleanup()                      # GPIO 핀들을 초기화
