import cv2 as cv
import numpy as np

hsv1 = 0
lower1 = 0
upper1 = 0
lower2 = 0
upper2 = 0
lower3 = 0
upper3 = 0
flag1=0

def nothing(x):
    pass


def mouse_callback(event, x, y, flags, param):
    global hsv1, flag1

    # 마우스 왼쪽 버튼 누를시 위치에 있는 픽셀값을 읽어와서 hsv1로 변환합니다.
    if event == cv.EVENT_LBUTTONDOWN:
       # print(img_color[y, x])
        color = img_color[y, x]

        one_pixel = np.uint8([[color]])     # numpy array 로 변환  3차원 배열로 변환
       # print(one_pixel)
        hsv1 = cv.cvtColor(one_pixel, cv.COLOR_BGR2HSV)          # [[[a b c]]] 3차원이지만 1차원에 1행 밖에 없는 행렬 생성 ==> 형식 맞춰주기 위해 hsv1[0][0]
        print(hsv1)
        hsv1 = hsv1[0][0] # 색값
        flag1=1

cv.namedWindow('img_color')
cv.setMouseCallback('img_color', mouse_callback)
cv.namedWindow('img_result')
cv.createTrackbar('thresholdLs1', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('thresholdLs1', 'img_result', 30)
cv.createTrackbar('thresholdUs1', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('thresholdUs1', 'img_result', 30)
cv.createTrackbar('thresholdLv1', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('thresholdLv1', 'img_result', 30)
cv.createTrackbar('thresholdUv1', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('thresholdUv1', 'img_result', 30)

cap = cv.VideoCapture(0, cv.CAP_V4L2)
cap.set(3, 320)
cap.set(4, 240)
while (True):
    # img_color = cv.imread('2.jpg')
    if flag1==1:
        thresholdLs1 = cv.getTrackbarPos('thresholdLs1', 'img_result')          #Ls
        thresholdLv1 = cv.getTrackbarPos('thresholdLv1', 'img_result')          #Lv
        thresholdUs1 = cv.getTrackbarPos('thresholdUs1', 'img_result')          #Us
        thresholdUv1 = cv.getTrackbarPos('thresholdUv1', 'img_result')          #Uv

        # hsv1 색공간에서 마우스 클릭으로 얻은 픽셀값과 유사한 필셀값의 범위를 정합니다.
        if hsv1[0] < 10:  #
            lower1 = np.array([hsv1[0] - 10 + 180, thresholdLs1, thresholdLv1])
            upper1 = np.array([180, thresholdUs1, thresholdUv1])
            lower2 = np.array([0, thresholdLs1, thresholdLv1])
            upper2 = np.array([hsv1[0], thresholdUs1, thresholdUv1])
            lower3 = np.array([hsv1[0], thresholdLs1, thresholdLv1])
            upper3 = np.array([hsv1[0] + 10, thresholdUs1, thresholdUv1])
        elif hsv1[0] > 170:
            # print("case2")
            lower1 = np.array([hsv1[0], thresholdLs1, thresholdLv1])
            upper1 = np.array([180, thresholdUs1, thresholdUv1])
            lower2 = np.array([0, thresholdLs1, thresholdLv1])
            upper2 = np.array([hsv1[0] + 10 - 180, thresholdUs1, thresholdUv1])
            lower3 = np.array([hsv1[0] - 10, thresholdLs1, thresholdLv1])
            upper3 = np.array([hsv1[0], thresholdUs1, thresholdUv1])
            #     print(i, 180, 0, i+10-180)
            #     print(i-10, i)
        else:
            # print("case3")                     # 그 밖의 부분은 경계를 구분할 필요가 없음.
            lower1 = np.array([hsv1[0], thresholdLs1, thresholdLv1])
            upper1 = np.array([hsv1[0]+10, thresholdUs1, thresholdUv1])
            lower2 = np.array([hsv1[0] - 10, thresholdLs1, thresholdLv1])
            upper2 = np.array([hsv1[0], thresholdUs1, thresholdUv1])
            lower3 = np.array([hsv1[0] - 10, thresholdLs1, thresholdLv1])
            upper3 = np.array([hsv1[0], thresholdUs1, thresholdUv1])


    ret, img_color = cap.read()             # frame 가로 *세로 *3 으로 표현
    height, width = img_color.shape[:2]     # 인덱스2 이전까지 ==> dimention, low만 표시 [0][1]  가로 240, 세로 320 필셀 존재
    img_color = cv.resize(img_color, (width, height), interpolation=cv.INTER_AREA)
  #  print(img_color.shape)             shape : 열의 수, 행의 수, 채널 수(색상 수)
    # 원본 영상을 hsv1 영상으로 변환합니다.

    img_hsv1 = cv.cvtColor(img_color, cv.COLOR_BGR2HSV)

    # 범위 값으로 hsv1 이미지에서 마스크를 생성합니다.
    img_mask1 = cv.inRange(img_hsv1, lower1, upper1)       # 범위가 음수인 경우는 재지정해줘야하기 때문에 범위를 3개로 나눔
    img_mask2 = cv.inRange(img_hsv1, lower2, upper2)       # 범위 지정 이진화 함수
    img_mask3 = cv.inRange(img_hsv1, lower3, upper3)
    img_mask = img_mask1 | img_mask2 | img_mask3

    kernel = np.ones((5, 5), np.uint8)                  # 모폴로지
    img_mask = cv.morphologyEx(img_mask, cv.MORPH_OPEN, kernel)
    img_mask = cv.morphologyEx(img_mask, cv.MORPH_CLOSE, kernel)

    # 마스크 이미지로 원본 이미지에서 범위값에 해당되는 영상 부분을 획득합니다.
    img_result = cv.bitwise_and(img_color, img_color, mask=img_mask)        #

    numOfLabels, _, stats, centroids = cv.connectedComponentsWithStats(img_mask)
    #print(centroids)
    for idx, centroid in enumerate(centroids):      # 한 row씩만 뽑아줌
        if stats[idx][0] == 0 and stats[idx][1] == 0:       # roi 이미지가 없으면 pass
            continue

        if np.any(np.isnan(centroid)):                  # ????
            continue

        x, y, width, height, area = stats[idx]             # stats는 2차원 배열에서  a[0]이면 1행만 출력!!
        centerX, centerY = int(centroid[0]), int(centroid[1])   #centerX, centerY = int(centroid[0]), int(centroid[1])??
      #  print(centerX, centerY)

        if area > 50:                                       # 크기가 50 이상이면 동그라미, 사각형인정
            cv.circle(img_color, (centerX, centerY), 10, (0, 0, 255), 10)
            cv.rectangle(img_color, (x, y), (x + width, y + height), (0, 0, 255))

    cv.imshow('img_color', img_color)
    cv.imshow('img_mask', img_mask)
    cv.imshow('img_result', img_result)

    # ESC 키누르면 종료
    if cv.waitKey(1) & 0xFF == 27:
        break

cv.destroyAllWindows()