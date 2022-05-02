#
#      공대선배 라즈베리파이썬 #6-2 PWM 출력2
#      youtube 바로가기: https://www.youtube.com/c/공대선배
#      LED가 서서히 밝아졌다가 서서히 어두워지는 코드
#

import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
import time                 # 시간관련 모듈을 불러옴

GPIO.setmode(GPIO.BCM)      # GPIO 핀들의 번호를 지정하는 규칙 설정

### 이부분은 아두이노 코딩의 setup()에 해당합니다
LED_pin = 2                     # LED 핀은 라즈베리파이 GPIO 2번핀으로 
GPIO.setup(LED_pin, GPIO.OUT)   # LED 핀을 출력으로 설정 : 아두이노의 pinmode와 같음
pwm = GPIO.PWM(LED_pin, 1000)   # LED 핀에 1000Hz의 PWM을 설정
pwm.start(0)                    # 처음 PWM 출력은 0으로 설정

### 이부분은 아두이노 코딩의 loop()에 해당합니다
try:                                    # 이 try 안의 구문을 먼저 수행하고
    while True:                         # 무한루프 시작: 아두이노의 loop()와 같음
        for ii in range(100):           # ii가 0~99 까지 총 100회의 for 루프
            pwm.ChangeDutyCycle(ii)     # 듀티싸이클을 ii로 설정
            time.sleep(0.01)            # 1/100초간 대기 (서서히 밝아짐)
        for ii in reversed(range(100)): # ii가 99~0까지 총 100회의 for 루프
            pwm.ChangeDutyCycle(ii)     # 듀티싸이클을 ii로 설정
            time.sleep(0.01)            # 1/100초간 대기 (서서히 어두워짐)

### 이부분은 반드시 추가해주셔야 합니다.
finally:                                # try 구문이 종료되면
    GPIO.cleanup()                      # GPIO 핀들을 초기화