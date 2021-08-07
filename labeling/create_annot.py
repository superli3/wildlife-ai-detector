import os
import json
from io import StringIO
import boto3
import s3fs
import pandas as pd


def annot_yolo(annot_file, cats):
    """
    Prepares the annotation in YOLO format

    Input:
    annot_file: csv file containing GroundTruth annotations
    ordered_cats: List of object categories in proper order for model training

    Returns:
    df_ann: pandas dataframe with the following columns
            img_file int_category box_center_w box_center_h box_width box_height


    Note:
    YOLO data format: <object-class> <x_center> <y_center> <width> <height>
    """

    df_ann = pd.read_csv(annot_file)

    df_ann["int_category"] = df_ann["category"].apply(lambda x: cats.index(x))
    df_ann["box_center_w"] = df_ann["box_left"] + df_ann["box_width"] / 2
    df_ann["box_center_h"] = df_ann["box_top"] + df_ann["box_height"] / 2

    # scale box dimensions by image dimensions
    df_ann["box_center_w"] = df_ann["box_center_w"] / df_ann["img_width"]
    df_ann["box_center_h"] = df_ann["box_center_h"] / df_ann["img_height"]
    df_ann["box_width"] = df_ann["box_width"] / df_ann["img_width"]
    df_ann["box_height"] = df_ann["box_height"] / df_ann["img_height"]

    return df_ann


def save_annots_to_s3(s3_bucket, prefix, df_local):
    """
    For every image in the dataset, save a text file with annotation in YOLO format

    Input:
    s3_bucket: S3 bucket name
    prefix: Folder name under s3_bucket where files will be written
    df_local: pandas dataframe with the following columns
              img_file int_category box_center_w box_center_h box_width box_height
    """

    unique_images = df_local["img_file"].unique()
    s3_resource = boto3.resource("s3")

    for image_file in unique_images:
        df_single_img_annots = df_local.loc[df_local.img_file == image_file]
        annot_txt_file = image_file.split(".")[0] + ".txt"
        destination = f"{prefix}/{annot_txt_file}"

        csv_buffer = StringIO()
        df_single_img_annots.to_csv(
            csv_buffer,
            index=False,
            header=False,
            sep=" ",
            float_format="%.4f",
            columns=[
                "int_category",
                "box_center_w",
                "box_center_h",
                "box_width",
                "box_height",
            ],
        )
        s3_resource.Object(s3_bucket, destination).put(Body=csv_buffer.getvalue())


def get_cats(json_file):
    """
    Makes a list of the category names in proper order

    Input:
    json_file: s3 path of the json file containing the category information

    Returns:
    cats: List of category names
    """

    filesys = s3fs.S3FileSystem()
    with filesys.open(json_file) as fin:
        line = fin.readline()
        record = json.loads(line)
        labels = [item["label"] for item in record["labels"]]

    return labels


def main():
    """
    Performs the following tasks:
    1. Reads input from 'input.json'
    2. Collect the category names from the GroundTruth job
    3. Creates a dataframe with annotaion in YOLO format
    4. Saves a text file in S3 with YOLO annotations
       for each of the labeled images
    """

    with open("input.json") as fjson:
        input_dict = json.load(fjson)

    s3_bucket = input_dict["s3_bucket"]
    job_id = input_dict["job_id"]
    gt_job_name = input_dict["ground_truth_job_name"]
    yolo_output = input_dict["yolo_output_dir"]

    s3_path_cats = (
        f"s3://{s3_bucket}/{job_id}/ground_truth_annots/{gt_job_name}/annotation-tool/data.json"
    )
    categories = get_cats(s3_path_cats)
    print("\n labels used in GroundTruth job: ")
    print(categories, "\n")

    gt_annot_file = "annot.csv"
    s3_dir = f"{job_id}/{yolo_output}"
    print(f"annotation files saved in = ", s3_dir)

    df_annot = annot_yolo(gt_annot_file, categories)
    save_annots_to_s3(s3_bucket, s3_dir, df_annot)


if __name__ == "__main__":
    main()
