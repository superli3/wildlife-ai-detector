# Labeling Tools
To label the videos we used AWS SageMaker Ground Truth. Unfortunately Ground Truth does not save annotations in Yolo format so additional transformations were required. 

AWS has published a [blog](https://aws.amazon.com/blogs/machine-learning/streamlining-data-labeling-for-yolo-object-detection-in-amazon-sagemaker-ground-truth/) and [sample code](https://github.com/aws-samples/groundtruth-object-detection) on github to convert the Ground Truth annotations to Yolo format. However, the samples only covered static images and not video files. The sample code did not work for annotating videos because the frames and annotations are spread across multiple directories (one for each video) so custom code was required to convert the annotations to Yolo format. 

We have modified the samples provided by AWS to work with their new video labeling capabilities. 

### Steps to convert Grond Truth Annotations to Yolo format:
1. **Clone AWS Repo** <br>
We started by cloning the AWS samples at https://github.com/aws-samples/groundtruth-object-detection.git`

2. **Install and AWS CLI and access keys**<br>
This code requires access to AWS to read and write to the AWS S3 bucket where your images and annotates are stored. Follow [these steps](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) to configure the CLI and your credentials.

3. **Edit input.json**<br>
This configuration file specifies where to find the annotations and image files created by Ground Truth. 

4. **Run parse_annots_video.py**<br>
We modified parse_annots.py to work with video labeling projects, which requiring walking through directories to find all of the files and annotations in a project. 

This steps saves all of the annotations into a single file ([annot.csv](annot.csv)), which is a prelimenary step before saving the annotations into yolo format. From this point forward the steps are the same as the samples provided by AWS. 

5. **Run create_annot.py** <>
This step will traverse the CSV and save labels in yolo format, which has one image per format. 

After the individual labels were created, they were split into train and test sets. The final set of images, labels, and yolo.yaml file are available for [download from AWS](https://hw05finalproject.s3.us-west-2.amazonaws.com/dataset2.zip).  


