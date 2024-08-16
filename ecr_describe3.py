import boto3
import csv
from botocore.exceptions import ClientError


def list_ecr_repositories(ecr_client):
    repositories = []
    paginator = ecr_client.get_paginator('describe_repositories')
    for page in paginator.paginate():
        repositories.extend(page['repositories'])
    return repositories


def count_images_and_calculate_storage(ecr_client, repository_name):
    image_count = 0
    total_size = 0
    paginator = ecr_client.get_paginator('describe_images')
    for page in paginator.paginate(repositoryName=repository_name):
        image_count += len(page['imageDetails'])
        for image in page['imageDetails']:
            if 'imageSizeInBytes' in image:
                total_size += image['imageSizeInBytes']
    return image_count, total_size


def check_lifecycle_policy(ecr_client, repository_name):
    try:
        ecr_client.get_lifecycle_policy(repositoryName=repository_name)
        return "Exists"
    except ClientError as e:
        if e.response['Error']['Code'] == 'LifecyclePolicyNotFoundException':
            return "Does Not Exist"
        else:
            raise


def main():
    profile = 'Shared-Services'
    region = 'eu-west-1'
    ecr_client = boto3.session.Session(profile_name=profile, region_name=region).client('ecr')
    repositories = list_ecr_repositories(ecr_client)
    counter = 1

    with open(f'ecr_{profile}_{region}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Repository Name', 'Number of Images', 'Total Storage (bytes)', 'Total Storage (GB)', 'Lifecycle Policy'])
        for repo in repositories:
            repo_name = repo['repositoryName']
            print(f"{counter}/{len(repositories)} Processing Repository: {repo_name}, ", end='')
            num_images, total_storage_bytes = count_images_and_calculate_storage(ecr_client, repo_name)
            total_storage_gb = round(total_storage_bytes / (1024 * 1024 * 1024), 2)
            print(f'num img: {num_images}, storage: {total_storage_gb}gb, ', end='')
            lifecycle_policy = check_lifecycle_policy(ecr_client, repo_name)
            print(f'lifecycle: {lifecycle_policy}')
            counter += 1
            writer.writerow([repo_name, num_images, total_storage_bytes, total_storage_gb, lifecycle_policy])


if __name__ == "__main__":
    main()
