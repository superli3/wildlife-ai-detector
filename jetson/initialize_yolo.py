import numpy as np
import base64
import paho.mqtt.client as mqtt
import time
import torch
import cv2
from PIL import Image
import pandas as pd
import shutil
import subprocess
from time import sleep
print('v1')
# Read in yolo model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

sleep(10)
#shutil.copy('yolov5s.pt','./root/.cache/torch/ultralytics_yolov5_master/yolov5s.pt')