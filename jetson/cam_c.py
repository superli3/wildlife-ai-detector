import numpy as np
import base64
import paho.mqtt.client as paho
import time
import torch
import cv2
import ssl
from PIL import Image
import pandas as pd
import shutil
import datetime


connflag = False

# func for establishing connection
def on_connect(client, userdata, flags, rc):                
    global connflag
    print("Connected to AWS")
    connflag = True
    #if connection is successful, rc value will be 0
    print("Connection returned result: " + str(rc) )
    #print(flags)

# Func for Sending msg
def on_message(client, userdata, msg):                      
    print(msg.topic+" "+str(msg.payload))
 
#def on_log(client, userdata, level, buf):
#    print(msg.topic+" "+str(msg.payload))

#create an mqtt client object
mqttc = paho.Client()    

#attach call back function
mqttc.on_connect = on_connect

# assign on_message func
mqttc.on_message = on_message                               

#### AWS Settings #### 
# Endpoint
awshost = "a1ug9vgksby7oq-ats.iot.us-west-1.amazonaws.com"  
# Connection port
awsport = 8883

 # Thing name
clientId = "W251-FP-YSJetson"                                    
thingName = "W251-FP-YSJetson"   
# Root_CA_Certificate_Name
caPath = "root-CA.crt"             

 # <Thing_Name>.cert.pem.crt. Thing's certificate from Amazon
certPath = "W251-FP-YSJetson.cert.pem"  

# <Thing_Name>.private.key Thing's private key from Amazon
keyPath = "W251-FP-YSJetson.private.key"        

# set parameters for mqqt aws transmission
mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)  

# connect to aws IOT server
mqttc.connect(awshost, awsport, keepalive=60)               

# Start MQTTC loop
mqttc.loop_start()                                         


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

            mqttc.publish("jetsoneventstopic", message, 1)     
            # Print sent msg to console
            print("Msg sent: ", message ) 

            cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),(255,255,0),2)
            cv2.putText(frame, row['name'] + " - " + str(row['confidence']) , (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
            roi_gray = frame[ymin:ymax, xmin:xmax]


    # Display the resulting frame
    cv2.imshow('frame', frame)

    captured_data = captured_data.append(frame_results_dataframe)
    #print(captured_data)
    # time.sleep(1)    

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break