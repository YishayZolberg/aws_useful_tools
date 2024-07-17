import boto3
import os
from tqdm import tqdm


def upload_file_multipart(file_name, bucket, object_name):
    boto3.setup_default_session(profile_name='profile-name')
    s3_client = boto3.client('s3', region_name='il-central-1')
    response = s3_client.create_multipart_upload(
        Bucket=bucket,
        Key=object_name
    )
    upload_id = response['UploadId']

    part_size = 8 * 1024 * 1024  # 8MB part size

    part_number = 1
    parts = []
    total_size = os.path.getsize(file_name)

    with open(file_name, 'rb') as file:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Uploading') as pbar:
            while True:
                # Read part data
                part_data = file.read(part_size)
                if not part_data:
                    break

                # Upload part
                response = s3_client.upload_part(
                    Bucket=bucket,
                    Key=object_name,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=part_data
                )
                parts.append({'PartNumber': part_number, 'ETag': response['ETag']})
                part_number += 1
                pbar.update(len(part_data))

    response = s3_client.complete_multipart_upload(
        Bucket=bucket,
        Key=object_name,
        UploadId=upload_id,
        MultipartUpload={'Parts': parts}
    )
    print("Upload completed successfully.")


file_name = 'file name'  # add full path if the file located in another location
bucket_name = 'bucket-name'
object_name = file_name
upload_file_multipart(file_name, bucket_name, object_name)
