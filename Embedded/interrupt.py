import RPI.GPIO as GPIO
BUTTON_GPIO = 27


CNT = 0
GPIO.setup(BUTTON_GPIO, GPIO.IN)
def button_callback():
    global CNT
    CNT +=1
    print(CNT)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.add_event_detect(BUTTON_GPIO, GPIO.RISING, button_callback)

