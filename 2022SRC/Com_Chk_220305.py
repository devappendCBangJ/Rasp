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

ser = serial.Serial(                # serial 객체
    port = '/dev/ttyAMA1',          # serial통신 포트
    baudrate = 115200,              # serial통신 속도
    parity = serial.PARITY_NONE,    # 패리티 비트 설정
    stopbits = serial.STOPBITS_ONE, # 스톱 비트 설정
    bytesize = serial.EIGHTBITS,    # 데이터 비트수
    timeout = 1                     # 타임 아웃 설정
    )

while True:
    cv_res = input('cv_res : \n')
    for i in range(len(cv_res)):
        # print(cv_res[i])
        ser.write(cv_res[i].encode())
        time.sleep(0.005)