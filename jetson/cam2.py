import torch
from PIL import Image

# Model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Image
img = 'https://ultralytics.com/images/zidane.jpg'

print(img)
img1 = Image.open('./zidane.jpeg')
print(img1)
# Inference
results = model(img1)
print(results.pandas().xyxy[0] )

for row in results.pandas().xyxy[0].iterrows():
    print(row)