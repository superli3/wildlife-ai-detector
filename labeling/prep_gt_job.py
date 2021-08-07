import boto3
import json


def create_manifest(job_path):
    """
    Creates the manifest file for the GroundTruth job

    Input:
    job_path: Full path of the folder in S3 for GT job

    Returns:
    manifest_file: The manifest file required for GT job
    """

    s3_rec = boto3.resource("s3")
    s3_bucket = job_path.split("/")[0]
    prefix = job_path.replace(s3_bucket, "")[1:]
    image_folder = f"{prefix}/images"
    print(f"using images from ... {image_folder} \n")

    bucket = s3_rec.Bucket(s3_bucket)
    objs = list(bucket.objects.filter(Prefix=image_folder))
    img_files = objs[1:]  # first item is the folder name
    n_imgs = len(img_files)
    print(f"there are {n_imgs} images \n")

    TOKEN = "source-ref"
    manifest_file = "/tmp/manifest.json"
    with open(manifest_file, "w") as fout:
        for img_file in img_files:
            fname = f"s3://{s3_bucket}/{img_file.key}"
            fout.write(f'{{"{TOKEN}": "{fname}"}}\n')

    return manifest_file


def upload_manifest(job_path, manifest_file):
    """
    Uploads the manifest file into S3

    Input:
    job_path: Full path of the folder in S3 for GT job
    manifest_file: Path to the local copy of the manifest file
    """

    s3_rec = boto3.resource("s3")
    s3_bucket = job_path.split("/")[0]
    source = manifest_file.split("/")[-1]
    prefix = job_path.replace(s3_bucket, "")[1:]
    destination = f"{prefix}/{source}"

    print(f"uploading manifest file to {destination} \n")
    s3_rec.meta.client.upload_file(manifest_file, s3_bucket, destination)


def main():
    """
    Performs the following tasks:
    1. Reads input from 'input.json'
    2. Collects image names from S3 and creates the manifest file for GT
    3. Uploads the manifest file to S3
    """

    with open("input.json") as fjson:
        input_dict = json.load(fjson)

    s3_bucket = input_dict["s3_bucket"]
    job_id = input_dict["job_id"]

    gt_job_path = f"{s3_bucket}/{job_id}"
    man_file = create_manifest(gt_job_path)
    upload_manifest(gt_job_path, man_file)


if __name__ == "__main__":
    main()
