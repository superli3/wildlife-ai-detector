# importing libraries
import paho.mqtt.client as paho
import ssl
from time import sleep
from random import uniform
import datetime
import uuid
import random

connflag = False

class MQTT_connector:
    def __init__(self):
        self.mqttc = None
        #self.connflag = False
    # func for establishing connection
    def on_connect(self, client, userdata, flags, rc):                
        global connflag
        print("Connected to AWS")
        connflag = True
        #if connection is successful, rc value will be 0
        print("Connection returned result: " + str(rc) )
        #print(flags)

    # Func for Sending msg
    def on_message(self, client, userdata, msg):                      
        print(msg.topic+" "+str(msg.payload))
    
    #def on_log(client, userdata, level, buf):
    #    print(msg.topic+" "+str(msg.payload))
    def establish_connect(self):
        #create an mqtt client object
        self.mqttc = paho.Client()    

        #attach call back function
        self.mqttc.on_connect = self.on_connect

        # assign on_message func
        self.mqttc.on_message = self.on_message                               

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
        self.mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)  

        # connect to aws IOT server
        self.mqttc.connect(awshost, awsport, keepalive=60)               


    def publish_message(self, message):
        self.mqttc.publish("jetsoneventstopic", message, 1) 
        print("Msg sent: ", message )                              
 
# while 1:
#     sleep(5)
#     if connflag == True:
#         eventid = str(uuid.uuid4())        
#         timeStamp = datetime.datetime.now()
#         classid = random.randint(0,10)
#         confidence = random.uniform(0,1)
#         classname = "tbd"
#         xmax = 1020.22
#         xmin = 415.95
#         ymax = 705.88
                
#         message = '{'+'"eventtimestamp":"'+str(timeStamp) + '",' + '"classid":"'+str(classid)+'",' + '"confidence":"'+str(confidence)+ '",' + '"name":"'+ str(classname) + '",' + '"xmax":"'+ str(xmax) + '",' + '"xmin":"' + str(xmin) + '",' + '"ymax":"'+ str(ymax) +'"}'
        
#         self.mqttc.publish("jetsoneventstopic", message, 1)     
#         # Print sent msg to console
#         print("Msg sent: ", message ) 
#     else:
#         print("waiting for connection...")       
        
