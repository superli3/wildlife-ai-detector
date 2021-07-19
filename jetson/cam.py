import numpy as np
import cv2
import base64
import paho.mqtt.client as mqtt
import time
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades  + 'haarcascade_frontalface_default.xml')

video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    #print(frame.shape)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    #count = 0
    for (x,y,w,h) in faces:

        #draw a border around the face
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,0),2)
        roi_gray = frame[y:y+h, x:x+w]

        #save the face as a base64 string to be emitted.
        face = frame[y:y+h, x:x+w] #slice the face from the image
        retval, buffer = cv2.imencode('.jpg', face)
        #print(jpg_as_text)

        #cv2.imwrite(str(count)+'.jpg', face)
        #count+=1

    # Display the resulting frame
    cv2.imshow('frame', frame)
      
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break