import boto3
import sys

def find_incomplete_multipart_uploads(region=None):
    # Initialize Boto3 AWS clients
    s3_client = boto3.client('s3', region_name=region)

    # Get all buckets in the AWS account
    response = s3_client.list_buckets()

    incomplete_uploads = []
    total_size = 0

    # Loop through each bucket and check for incomplete multipart uploads
    for bucket_info in response['Buckets']:
        bucket_name = bucket_info['Name']
        bucket_response = s3_client.list_multipart_uploads(Bucket=bucket_name)
        
        # Check if there are incomplete uploads in the bucket
        if 'Uploads' in bucket_response:
            for upload in bucket_response['Uploads']:
                key = upload['Key']
                incomplete_uploads.append((bucket_name, key))

    return incomplete_uploads

if __name__ == "__main__":
    # Get region from command line argument, or use default region from AWS CLI configuration
    region = sys.argv[1] if len(sys.argv) > 1 else boto3.Session().region_name

    incomplete_uploads = find_incomplete_multipart_uploads(region)
    
    if incomplete_uploads:
        print("Incomplete Amazon S3 Multi-part Uploads in region {}: ".format(region))
        for bucket_name, key in incomplete_uploads:
            print("- Bucket: {}, Key: {}".format(bucket_name, key))
    else:
        print("No incomplete Amazon S3 Multi-part Uploads found in region {}.".format(region))
