from io import StringIO
import json
import s3fs
import boto3
import pandas as pd


def parse_gt_output(manifest_path, s3_bucket, job_id, custom_job_name):
    """
    Captures the json GroundTruth bounding box annotations into a pandas dataframe

    Input:
    manifest_path: S3 path to the annotation file
    job_name: name of the GroundTruth job

    Returns:
    df_bbox: pandas dataframe with bounding box coordinates
             for each item in every image
    """
    s3_resource = boto3.resource("s3")
    filesys = s3fs.S3FileSystem()
    with filesys.open(manifest_path) as fin:
        annot_list = []
        for line in fin.readlines():
            record = json.loads(line)
            if custom_job_name in record.keys():  # is it necessary?
                image_file_path = record["source-ref"]
                image_file_name = image_file_path.split("/")[-1]
                class_maps = record[f"{custom_job_name}-metadata"]["class-map"]

                #imsize_list = record[custom_job_name]["image_size"]
                #assert len(imsize_list) == 1
                image_width = 1920
                image_height = 1080

                frames_json_path = record[custom_job_name]

                with filesys.open(frames_json_path, 'r') as file:
                    frames_json = json.load(file)

                    frames_with_annotations = len(frames_json["detection-annotations"])
                    for i in range(0,frames_with_annotations):
                        annot = frames_json["detection-annotations"][i]

                        frame_file_name = image_file_path.split("/")[5].replace(".mp4", "-" + annot["frame"]) 
                        source_file_path = image_file_path.replace(image_file_name, frames_json["detection-annotations"][i]['frame'])
                        destination_file_path = f"{job_id}/yolo_images/{frame_file_name}"
                        
                        s3_resource.Object(s3_bucket, destination_file_path).copy_from(
                            CopySource=source_file_path.replace("s3://",""))
                        
                        
                        #        destination = f"{prefix}/{annot_txt_file}"
                        #s3_resource.Object(s3_bucket, destination)

                        num_annotations = len(annot["annotations"])
                        for i in range(0, num_annotations):
                            class_name = class_maps[f'{annot["annotations"][i]["class-id"]}']
                            left = annot["annotations"][i]["left"]
                            top = annot["annotations"][i]["top"]
                            height = annot["annotations"][i]["height"]
                            width = annot["annotations"][i]["width"]
                            
                            if annot["annotations"][i]["class-id"] in ['0','1']:

                                annot_list.append(
                                    [
                                        frame_file_name,
                                        class_name,
                                        left,
                                        top,
                                        height,
                                        width,
                                        image_width,
                                        image_height,
                                    ]
                                )

    df_bbox = pd.DataFrame(
        annot_list,
        columns=[
            "img_file",
            "category",
            "box_left",
            "box_top",
            "box_height",
            "box_width",
            "img_width",
            "img_height",
        ],
    )

    return df_bbox

def save_df_to_s3(df_local, s3_bucket, destination):
    """
    Saves a pandas dataframe to S3

    Input:
    df_local: Dataframe to save
    s3_bucket: Bucket name
    destination: Prefix
    """

    csv_buffer = StringIO()
    s3_resource = boto3.resource("s3")

    df_local.to_csv(csv_buffer, index=False)
    s3_resource.Object(s3_bucket, destination).put(Body=csv_buffer.getvalue())


def main():
    """
    Performs the following tasks:
    1. Reads input from 'input.json'
    2. Parses the GroundTruth annotations and creates a dataframe
    3. Saves the dataframe to S3
    """

    with open("input.json") as fjson:
        input_dict = json.load(fjson)

    s3_bucket = input_dict["s3_bucket"]
    job_id = input_dict["job_id"]
    gt_job_name = input_dict["ground_truth_job_name"]
    custom_job_name = input_dict["custom_job_name"]

    mani_path = f"s3://{s3_bucket}/{job_id}/ground_truth_annots/{gt_job_name}/manifests/output/output.manifest"

    df_annot = parse_gt_output(mani_path, s3_bucket, job_id, custom_job_name)
    dest = f"{job_id}/ground_truth_annots/{gt_job_name}/annot.csv"
    save_df_to_s3(df_annot, s3_bucket, dest)

if __name__ == "__main__":
    main()
