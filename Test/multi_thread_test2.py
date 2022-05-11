import time
#import serial
import cv2
import numpy as np
# import RPi.GPIO as GPIO
import threading
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

W_View_size = 400
H_View_size = 300

lower_green = (36, 72, 78)
upper_green = (70, 255, 219)
#blue
lower_blue = (103, 170, 80)
upper_blue = (110, 255, 194)
#red
lower_red = (173, 109, 150)
upper_red = (175, 232, 230)

# 원통 크기 기준, 통신 데이터 리스트
green_small = W_View_size * H_View_size * 0.0005
green_middle = W_View_size * H_View_size * 0.0025
green_big = W_View_size * H_View_size * 0.005834


FPS1 = list()
FPS2 = list()

kernel = np.ones((5, 5), np.uint8)

class camThread(threading.Thread):
    def __init__(self, camName, camID):
        threading.Thread.__init__(self)
        self.camName = camName
        self.camID = camID

    def run(self):
        print("Starting" + self.camName)
        camOperate(self.camName, self.camID)


def camOperate(camName, camID):
    cv2.namedWindow(camName)
    cam = cv2.VideoCapture(camID, cv2.CAP_V4L2)
    if not cam.isOpened():  # try to get the first frame
        print(camID)
        return
    if(camID==0):
        while True:
            print("0도라")
            ret, frame = cam.read()
            if not ret:
                continue
            frame = cv2.resize(frame, dsize=(
                W_View_size, H_View_size), interpolation=cv2.INTER_AREA)
            img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            bin_image1 = Masking(img_hsv, lower_green, upper_green)
            bin_image2 = Masking(img_hsv, lower_blue, upper_blue)
            bin_image4 = bin_image1 | bin_image2

            '''
            #컨투어
            contours_green, _ = cv2.findContours(
                bin_image1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours_blue, _ = cv2.findContours(
                bin_image2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            max_areaG, max_contourG = get_contour(contours_green)
            #max_areaR, max_contourR = get_contour(contours_red)
            #max_areaB, max_contourB = get_contour(contours_blue)
            gx, gy, gw, gh = cv2.boundingRect(max_contourG)
            #rx, ry, rw, rh = cv2.boundingRect(max_contourR)
            #bx, by, bw, bh = cv2.boundingRect(max_contourB)
            centerX, centerY = gx+gw/2, gy+gh/2

            cv2.rectangle(bin_image4, (gx, gy), (gx+gw, gy+gh), (255, 0, 0), 2)
            '''
            cv2.imshow(camName,frame)

            '''
            ras_res = ""
            if(len(contours_green) != 0):  # contours 존재하면
                if(max_areaG < green_small):
                    if(centerX < W_View_size * 3.5 / 11):
                        ras_res += "1,1"
                    elif(W_View_size * 3.5 / 11 <= centerX <= W_View_size * 7.5 / 11):
                        ras_res += "2,1"
                    elif(W_View_size * 7.5 / 11 < centerX):
                        ras_res += "3,1"
                elif(green_small <= max_areaG <= green_middle):
                    if(centerX < W_View_size * 3 / 11):
                        ras_res += "1,2"
                    elif(W_View_size * 3 / 11 <= centerX <= W_View_size * 8 / 11):
                        ras_res += "2,2"
                    elif(W_View_size * 8 / 11 < centerX):
                        ras_res += "3,2"
                elif(green_middle <= max_areaG <= green_big):
                    if(centerX < W_View_size * 2.5 / 11):
                        ras_res += "1,3"
                    elif(W_View_size * 2.5 / 11 <= centerX <= W_View_size * 8.5 / 11):
                        ras_res += "2,3"
                    elif(W_View_size * 8.5 / 11 < centerX):
                        ras_res += "3,3"
                elif(green_big < max_areaG):
                    if(centerX < W_View_size * 3 / 11):
                        ras_res += "1,4"
                    elif(W_View_size * 3 / 11 <= centerX <= W_View_size * 8 / 11):
                        ras_res += "2,4"
                    elif(W_View_size * 8 / 11 < centerX):
                        ras_res += "3,4"
            else:  # contours 없으면
                ras_res += "9,9"
            ras_res += ",9/"

            ser.write(ras_res.encode())
            '''
            key = cv2.waitKey(20)
            if key == 27:  # exit on ESC
                break        
    else:
        while True:
            print("1도라")
            ret, frame = cam.read()
            if not ret:
                continue
            frame = cv2.resize(frame, dsize=(
                400, 300), interpolation=cv2.INTER_AREA)
            img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            bin_image = Masking(img_hsv, lower_red, upper_red)
            
            '''
            contours_red, _ = cv2.findContours(
                bin_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            max_areaR, max_contourR = get_contour(contours_red)
            rx, ry, rw, rh = cv2.boundingRect(max_contourR)


            cv2.rectangle(bin_image, (rx, ry), (rx+rw, ry+rh), (255, 0, 0), 2)
            '''
            cv2.imshow(camName, frame)
            key = cv2.waitKey(20)
            if key == 27:  # exit on ESC
                break
    cam.release()
    cv2.destroyWindow(camName)

'''
# 카메라 설정, 화면 사이즈, hsv
# cap = cv2.VideoCapture(cv2.CAP_DSHOW + 1)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
W_View_size = 400
H_View_size = 300
#cap.set(3, W_View_size)
#cap.set(4, H_View_size)
'''


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

'''
def check_fps(start,end):
    sec = end-start
    fps1 = 1/sec
    FPS1.append(fps1)
    count1 = count1+1
    if(count1 == 20):
        print("평균 fps1:", np.mean(FPS1))
        FPS1 = []
        count1 = 0
'''


# Create two threads as follows

thread1 = camThread("Camera 1", 0)
thread2 = camThread("Camera 2", 1)
thread1.start()
thread2.start()
