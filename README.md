# Wildlife detection.

This repo contains the final project involving wildlife detection for w251, which encompasses wildlife detection

Contributors: Alex Heaton, Jeff Li, Tina Huang, Yuriy Shevchenko

## Project Inspiration and Overview
In this project we used deep learning (computer vision) to automate animal monitoring to generate insights that can be acted upon by humans or another computer process. 

## Potential Applications 
Using AI to monitor animal behavior can be used to aid animal preservation and develop new business opportunities. 

Our research was motivated by monitoring live camera feed that is installed at Big Bear Lake, CA to monitor California Bald Eagles nest. The site was monitored 24 hours a day but the project relied on humans to monitor the feed and manually record the activity. The year the eagles laid eggs but they did not survive and the researchers do not know the reason. Potentially by using AI to create a larger scale monitoring program researchers could understand the behavior and conditions that would help more wildlife survive. 

In commercial applications, we see an increase in smart pet products using AI to create automated cat feeders, bird feeders that identify birds, and robots that will follow your pet to monitor them and keep them company.  

## Solutions Overview 
![image](/images/0.png)
Our goal was to create an end-to-end workflow that could be followed by others to accomplish similar tasks. he steps of this workflow are to
Collect video recordings (data)
Label video frames
Train custom Yolo model
Perform object detection on Jetson using live video 
Send output to the cloud for analysis 

At the end of the project we were able to deploy an object detection model that can run on an edge device to identify squirrels and nuts in a live video feed.
## Dataset
We trained our model using a custom dataset of videos we recorded at a site where squirrels often come to feed. We placed nuts outside the window and captured squirrels and birds that came to the window to pick up nuts.

### Data Collection
We collected several weeks of sample videos that we used to develop our model. To collect the videos we used the Shinobi open source CCTV monitoring software installed on a Jetson device, which was monitoring the stream from an IP camera pointed at the feeding area. 

Shinobi has built-in motion detection capabilities that we configured and tuned so that video would only be recorded when a squirrel came to visit. This limited the time that we needed to spend watching video recordings looking for relevant frames of squirrel activity. While motion is detected, Shinobi would automatically start recording the video and then save it to an AWS S3 storage bucket. We captured over 100 videos. 
### Data Labeling & Annotation 
To label the videos we used AWS SageMaker Ground Truth. Ground truth has several powerful features that led us to use that tool. 
User friendly UI for drawing bounding boxes that can work with files stored in S3 and store the labels back to S3.  
Split video files into frames (using FFmpeg behind the scenes). 
Distribute labeling tasks amongst team members. 
Convert Labels to Yolo v5 Format
The one con of Ground Truth was that it saves the labels in a proprietary format and additional transformations are required to convert it to the Yolo format. AWS has published a blog and sample code on github to convert the Ground Truth annotations to Yolo format. However, the samples only covered static images and not video files. The sample code did not work for annotating videos because the frames and annotations are spread across multiple directories (one for each video) so custom code was required to convert the annotations to Yolo format. We plan to make this code available to others who need to label videos in Ground Truth. 

## Model 

![image](/images/1.png)
We divided the labeled images into 70% (219) training, 20% (63) validation, and 10% (31) testing sets and used the images collected to retrain the YOLOv5 model. We trained the model on Google Colab with GPU using Roboflow custom YOLOv5 notebook. We choose YOLOv5s because its small size can reduce space required on the Jetson and lower running time. 

We made improvements using augmentation including grey scale and angle change. We also improved the model performance by increasing training time from 100 epochs to 300 epochs to 1000 epochs. 
(See below figure for 100 epochs training stats)


We saw noticeable improvement from 300 epochs to 1000 epochs. Below is an example of a testing image. The left image is with the inference result of 300 epochs, in which only the nuts are detected but not the squirrel. The right image is the same image but with the inference result of 1000 epochs, in which both squirrel and nuts are detected.

![image](/images/2.png) ![image](/images/3.png)

We reached 0.803 for overall precision, 0.829 for squirrel class precision, and 0.777 for nut class precision.

(See below table for final model stats)

Class | Squirrel | Nut | All
------|-------|---------|--------
Precision | 0.829 | 0.777 | 0.803
Recall | 0.894 | 0.817 | 0.856
mAP@.5 | 0.878 | 0.84 | 0.859
mAP@.5:.95 | 0.473 | 0.255 | 0.364





## Jetson/Model Implementation

## Jetson deployment
Our intention was to implement the model onto a Nvidia Jetson NX. The NX is a lightweight device that will run the model continuously and perform inference based on video coming in over the local network.

We utilized a Docker file to standardize deployments across numerous Jetson devices. The container is based off of Nvidia’s L4T. Inference is then performed across each frame. 

If an object has been detected in the frame, we utilize MQTT messaging to send a result of the captured object to AWS.


## Integration Architecture

![image](/images/4.png)



## AWS IoT MQTT Broker

Amazon Internet of Things is a cloud based service that provides a convenient integration solution to connect any smart devices such as Jetson and others to other AWS and cloud services.   

In this project we are utilizing AWS IoT Mosquitto Broker service to capture all events that are published for jetsoneventstopic and store them in the cloud repository for further processing and analysis. 

Here is the format of the data that MQTT Broker receives from Jetson:

![image](/images/5.png)

## AWS DynamoDB

Amazon DynamoDB is a key-value and document-based high performance database that is easily scalable and fully managed on the cloud. It fits our purpose perfectly to capture and store triggered events from Jetson for further review and analysis.

![image](/images/6.png)

As a key for each record, it was decided to utilize a timestamp of the triggered event and use Class Id of the event as a sorting key in DynamoDB. The rest of the data is stored as a payload text in a JSON format.


![image](/images/7.png)

## Results Review

![image](/images/8.png)
![image](/images/9.png)


## Future Improvements

-Change model to lite to speed up inference

-Standardize labeling & increase training data set  for better accuracy

-Expand to other wild animals

-Train models to recognize animal faces to separate animals of the same species

-Train model to recognize food consumption

-Overlay collected data with public weather and air quality data for patterns recognition

-Connect to an automated feeding system to feed when all nuts are gone 


## References
-Shinobi Open Source CCTV Solution https://shinobi.video/ 

-Roboflow-Custom-YOLOv5: https://colab.research.google.com/drive/1gDZ2xcTOgR39tGGs-EZ6i3RTs16wmzZQ







