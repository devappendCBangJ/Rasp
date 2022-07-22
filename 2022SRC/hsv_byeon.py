import cv2 as cv
import numpy as np
import pyrealsense2
from realsense_depth import *

hsv= [0,0,0,0,0]
lower_blue1 = 0
upper_blue1 = 0
lower_blue2 = 0
upper_blue2 = 0
lower_blue3 = 0
upper_blue3 = 0
centerX=400
centerY=300
point = (centerX, centerY)
areavs=0
def nothing(x):
    pass


def mouse_callback(event, x, y, flags, param):
    global hsv, lower_blue1, upper_blue1, lower_blue2, upper_blue2, lower_blue3, upper_blue3, threshold

    # 마우스 왼쪽 버튼 누를시 위치에 있는 픽셀값을 읽어와서 HSV로 변환합니다.
    if event == cv.EVENT_LBUTTONDOWN:
        #print(img_color[y, x])

        for i in [-1,0,1]:
            for j in [-1,0,1] :
                #print(i,j,img_color[y+j, x+i])
                color = img_color[y+j, x+i]
                one_pixel = np.uint8([[color]])
                hsv = cv.cvtColor(one_pixel, cv.COLOR_BGR2HSV)
                #print(hsv[0])


        print(hsv[0])
        hsv = hsv[0][0]


        # HSV 색공간에서 마우스 클릭으로 얻은 픽셀값과 유사한 필셀값의 범위를 정합니다.

            #     print(i, i+10)
            #     print(i-10, i)


        # print("@1", lower_blue1, "~", upper_blue1)
        # print("@2", lower_blue2, "~", upper_blue2)
        # print("@3", lower_blue3, "~", upper_blue3)


cv.namedWindow('img_color')
cv.setMouseCallback('img_color', mouse_callback)
thu=30
thd=255
th2u=30
th2d=255
cv.namedWindow('img_result')
cv.createTrackbar('threshold', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('threshold', 'img_result', thu)
cv.createTrackbar('thresholdd', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('thresholdd', 'img_result', thd)
cv.createTrackbar('threshold2', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('threshold2', 'img_result', th2u)
cv.createTrackbar('threshold22', 'img_result', 0, 255, nothing)
cv.setTrackbarPos('threshold22', 'img_result', th2d)

cap = cv.VideoCapture(2)
cap.set(3, 640)
cap.set(4, 480)
#Create mouse event
while (True):
    # img_color = cv.imread('2.jpg')


    ret, img_color = cap.read()
    height, width = img_color.shape[:2]
    threshold = cv.getTrackbarPos('threshold', 'img_result')
    threshold2 = cv.getTrackbarPos('threshold2', 'img_result')
    thresholdd = cv.getTrackbarPos('thresholdd', 'img_result')
    threshold22 = cv.getTrackbarPos('threshold22', 'img_result')
    if hsv[0] < 10:
        #print("case1")
        lower_blue1 = np.array([hsv[0] - 10 + 180, threshold, threshold2])
        upper_blue1 = np.array([180, thresholdd, threshold22])
        lower_blue2 = np.array([0, threshold, threshold2])
        upper_blue2 = np.array([hsv[0], thresholdd, threshold22])
        lower_blue3 = np.array([hsv[0], threshold, threshold2])
        upper_blue3 = np.array([hsv[0] + 10, thresholdd, threshold22])
        #     print(i-10+180, 180, 0, i)
        #     print(i, i+10)

    elif hsv[0] > 170:
       #print("case2")
        lower_blue1 = np.array([hsv[0], threshold, threshold2])
        upper_blue1 = np.array([180, thresholdd, threshold22])
        lower_blue2 = np.array([0, threshold, threshold2])
        upper_blue2 = np.array([hsv[0] + 10 - 180, thresholdd, threshold22])
        lower_blue3 = np.array([hsv[0] - 10, threshold, threshold2])
        upper_blue3 = np.array([hsv[0], thresholdd, threshold22])
        #     print(i, 180, 0, i+10-180)
        #     print(i-10, i)
    else:
       # print("case3")
        lower_blue1 = np.array([hsv[0], threshold, threshold2])
        upper_blue1 = np.array([hsv[0] + 10, thresholdd, threshold22])
        lower_blue2 = np.array([hsv[0] - 10, threshold, threshold2])
        upper_blue2 = np.array([hsv[0], thresholdd, threshold22])
        lower_blue3 = np.array([hsv[0] - 10, threshold, threshold2])
        upper_blue3 = np.array([hsv[0], thresholdd, threshold22])
    # 원본 영상을 HSV 영상으로 변환합니다.
    img_hsv = cv.cvtColor(img_color, cv.COLOR_BGR2HSV)

    # 범위 값으로 HSV 이미지에서 마스크를 생성합니다.
    img_mask1 = cv.inRange(img_hsv, lower_blue1, upper_blue1)
    img_mask2 = cv.inRange(img_hsv, lower_blue2, upper_blue2)
    img_mask3 = cv.inRange(img_hsv, lower_blue3, upper_blue3)
    img_mask = img_mask1 | img_mask2 | img_mask3

    kernel = np.ones((2, 2), np.uint8)
    img_mask = cv.morphologyEx(img_mask, cv.MORPH_OPEN, kernel)
    img_mask = cv.morphologyEx(img_mask, cv.MORPH_CLOSE, kernel)

    # 마스크 이미지로 원본 이미지에서 범위값에 해당되는 영상 부분을 획득합니다.
    img_result = cv.bitwise_and(img_color, img_color, mask=img_mask)

    numOfLabels, img_label, stats, centroids = cv.connectedComponentsWithStats(img_mask)
    areavs = 0
    centervsX = 0
    centervsY = 0
    for idx, centroid in enumerate(centroids):
        if stats[idx][0] == 0 and stats[idx][1] == 0:
            continue

        if np.any(np.isnan(centroid)):
            continue

        x, y, width, height, area = stats[idx]
        centerX, centerY = int(centroid[0]), int(centroid[1])
        # print(centerX, centerY)


            # cv.rectangle(img_color, (x, y), (x + width, y + height), (0, 0, 255))
        if area > areavs :
            centervsX = centerX
            centervsY = centerY
            areavs = area
    cv.circle(img_color, (centervsX, centervsY), 10, (0, 0, 255), 10)
    cv.imshow('img_color', img_color)
    cv.imshow('img_mask', img_mask)
    cv.imshow('img_result', img_result)

    # ESC 키누르면 종료
    if cv.waitKey(1) & 0xFF == 27:
        break
    # ret2, depth_frame, color_frame = dc.get_frame()
    #
    # cv.circle(color_frame, point, 4, (0, 0, 255))
    # distance = depth_frame[point[1], point[0]]
    #
    # cv.putText(color_frame, "{}mm".format(distance), (point[0], point[1]), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
    #
    # cv.imshow("depth frame", depth_frame)
    # cv.imshow("Color frame", color_frame)
    key = cv.waitKey(1)


cv.destroyAllWindows()