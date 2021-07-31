import numpy as np
import base64
import paho.mqtt.client as mqtt
import time
import torch
import cv2
from PIL import Image
import pandas as pd
import shutil
import datetime
from publisher import MQTT_connector


test = MQTT_connector()
print(test)
print(test.mqttc)
test.establish_connect()
test.publish_message('blah')
#publisher1.establish_connect()
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

#face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades  + 'haarcascade_frontalface_default.xml')


#model = cv2.dnn.readNetFromONNX('/Users/jeff/documents/mids/w251/yolov5/yolov5s.onnx')
#print(torch.cuda.is_available())
#print(torch.cuda.device_count())
#print(torch.cuda.get_device_name(0))
video_capture = cv2.VideoCapture(0)

#empty dataframe to append to
captured_data = pd.DataFrame()

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    #print(frame.shape)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #convert frame into format that mdoel can interpret
    PIL_image = Image.fromarray(frame)
    results = model(PIL_image)
    #preds = model.forward()

    frame_results_dataframe = results.pandas().xyxy[0]

    if len(frame_results_dataframe) > 0:
        frame_results_dataframe['time'] = time.strftime("%H:%M:%S", time.localtime())

        #draw objects around frame

        timeStamp = datetime.datetime.now()
        for index, row in frame_results_dataframe.iterrows():
            xmin = int(row['xmin'])
            xmax = int(row['xmax'])
            ymin = int(row['ymin'])
            ymax = int(row['ymax'])


            message = '{'+'"eventtimestamp":"'+str(timeStamp) + '",' + '"classid":"'+str(row['class'])+'",' + '"confidence":"'+str(row['confidence'])+ '",' + '"name":"'+ str(row['name']) + '",' + '"xmax":"'+ str(row['xmax']) + '",' + '"xmin":"' + str(row['xmin']) + '",' + '"ymax":"'+ str(row['ymax']) +'"}'

            test.publish_message(message)

            cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),(255,255,0),2)
            cv2.putText(frame, row['name'] + " - " + str(row['confidence']) , (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
            roi_gray = frame[ymin:ymax, xmin:xmax]


    # Display the resulting frame
    cv2.imshow('frame', frame)

    captured_data = captured_data.append(frame_results_dataframe)
    print(captured_data)
    # time.sleep(1)    

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break