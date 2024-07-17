import boto3
from tqdm import tqdm
import botocore.exceptions


def remove_all_objects(bucket_name, session):
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)

# this part for delete versioning only. it's not necessary!
    # object_versions = []
    # for obj_version in bucket.object_versions.all():
    #     object_versions.append({'Key': obj_version.object_key, 'VersionId': obj_version.id})
    #
    # # Delete all versions of objects in batches of 1000
    # for i in range(0, len(object_versions), 1000):
    #     delete_objects_batch = {'Objects': object_versions[i:i + 1000]}
    #     bucket.delete_objects(Delete=delete_objects_batch)
# if the versioning part is running you can pass the following code:

    total_objects = sum(1 for _ in bucket.objects.all())
    with tqdm(total=total_objects, desc=f"Deleting objects in bucket {bucket_name}") as pbar:
        for obj in bucket.objects.all():
            obj.delete()
            pbar.update(1)


def delete_all_buckets(session):
    s3 = session.resource('s3')
    not_deleted = 0
    for bucket in s3.buckets.all():
        try:
            bucket_region = s3.meta.client.get_bucket_location(Bucket=bucket.name)['LocationConstraint']
            session = boto3.Session(profile_name='wetask', region_name=bucket_region)
            remove_all_objects(bucket.name, session)
            bucket.delete()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'BucketNotEmpty':
                not_deleted += 1
                print(f"Bucket {bucket.name} is not empty. Skipping deletion.")
                print("You can uncomment the code part for delete objects versions")
            else:
                raise
    print(f"{not_deleted} buckets not deleted.")


def main():
    profile_name = 'wetask'
    session = boto3.Session(profile_name=profile_name)
    s3 = session.resource('s3')
    print('Your s3 buckets:')
    counter = 0
    for bucket in s3.buckets.all():
        counter += 1
    if counter == 0:
        print("no s3 bucket in the account")
    else:
        print(f"You have {counter} buckest:")
        counter = 0
        for bucket in s3.buckets.all():
            counter += 1
            print(f'{counter}: {bucket}')
        confirmation = input(
            "This action will delete all S3 objects and buckets. Are you sure you want to proceed? (yes/no): ")
        if confirmation.lower() != "yes":
            print("Operation cancelled.")
            return

        delete_all_buckets(session)
        print("All S3 objects and buckets have been deleted.")

if __name__ == "__main__":
    main()