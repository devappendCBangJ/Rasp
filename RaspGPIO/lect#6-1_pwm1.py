#
#      공대선배 라즈베리파이썬 #6-1 PWM 출력1
#      youtube 바로가기: https://www.youtube.com/c/공대선배
#      LED가 단계적으로 밝아지는 코드
#

import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
import time                 # 시간관련 모듈을 불러옴

GPIO.setmode(GPIO.BCM)      # GPIO 핀들의 번호를 지정하는 규칙 설정

### 이부분은 아두이노 코딩의 setup()에 해당합니다
LED_pin = 2                     # LED 핀은 라즈베리파이 GPIO 2번핀으로 
GPIO.setup(LED_pin, GPIO.OUT)   # LED 핀을 출력으로 설정 : 아두이노의 pinmode와 같음
pwm = GPIO.PWM(LED_pin, 1000)   # LED 핀에 1000Hz의 PWM을 설정. GPIO 라이브러리에서 하드웨어적으로 PWM을 사용할 수 없지만, 소프트웨어적으로 빠르게 on/off 제어 반복으로 구현 가능
pwm.start(0)                    # 처음 PWM 출력은 0으로 설정

### 이부분은 아두이노 코딩의 loop()에 해당합니다
try:                                    # 이 try 안의 구문을 먼저 수행하고
    while True:                         # 무한루프 시작: 아두이노의 loop()와 같음
        pwm.ChangeDutyCycle(0)          # pwm의 듀티사이클을 0%로(LED 끔) : 아두이노의 analogwrite와 같음
        time.sleep(1)                   # 1초간 대기
        pwm.ChangeDutyCycle(25)         # 듀티사이클을 25%로(LED 밝기 25%) : 아두이노의 analogwrite와 같음
        time.sleep(1)                   # 1초간 대기
        pwm.ChangeDutyCycle(50)         # 듀티사이클을 50%로(LED 최대의 절반밝기로) : 아두이노의 analogwrite와 같음
        time.sleep(1)                   # 1초간 대기
        pwm.ChangeDutyCycle(75)         # 듀티사이클을 75%로(LED 밝기 75%) : 아두이노의 analogwrite와 같음
        time.sleep(1)                   # 1초간 대기
        pwm.ChangeDutyCycle(100)        # 듀티사이클을 100%로(LED 최대밝기) : 아두이노의 analogwrite와 같음
        time.sleep(1)                   # 1초간 대기

### 이부분은 반드시 추가해주셔야 합니다.
finally:                                # try 구문이 종료되면
    GPIO.cleanup()                      # GPIO 핀들을 초기화