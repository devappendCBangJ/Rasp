time1=0
time2=0
Check_fps=deque(np.zeros(100))
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


#ang = 90


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
        #print(area)
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
            #print(ras_res)
    #elif((centerX!=0 and centerY!=0) and (len(contours) ==0)): 여기서 좀 더 세부적으로 나눌거임.
        #ras_res += "9,9"
    else: #contours 없으면
        ras_res += "9,9"
        #print(ras_res)
    ras_res += ",9/"
    
    #servo_move(ang)

    ser.write(ras_res.encode())


    #cv2.imshow('frame', frame)
    
    cv2.imshow('dst', bin_image)
    time2 = time.time()
    
    sec = time2-time1
    fps = 1/sec
    
    Check_fps.append(fps)
    Check_fps.popleft()
    
    average=np.mean(Check_fps)    
    print(average)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

#GPIO.cleanup()