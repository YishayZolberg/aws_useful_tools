import boto3
import csv
from collections import defaultdict
from datetime import datetime, timedelta

PROFILE_NAME = 'profile-name'
def get_expire_date(ri):
    start_date = ri['Start']
    duration = ri['Duration']
    expire_date = start_date + timedelta(seconds=duration)
    return expire_date

def sum_active_ri_by_expiry_and_type():
    ec2_client = boto3.session.Session(profile_name=PROFILE_NAME, region_name='us-east-1').client('ec2')
    reserved_instances = ec2_client.describe_reserved_instances(Filters=[{'Name': 'state', 'Values': ['active']}])
    ri_sum_by_expiry_and_type = defaultdict(lambda: defaultdict(int))
    for ri in reserved_instances['ReservedInstances']:
        expire_date = get_expire_date(ri)
        expire_date_str = expire_date.strftime('%Y-%m-%d')
        instance_type = ri['InstanceType']
        ri_sum_by_expiry_and_type[expire_date_str][instance_type] += ri['InstanceCount']

    with open('aws_ri_sum_by_expiry_and_type.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ExpirationDate', 'InstanceType', 'TotalInstances'])
        for expire_date, instance_types in ri_sum_by_expiry_and_type.items():
            for instance_type, total_instances in instance_types.items():
                writer.writerow([expire_date, instance_type, total_instances])


if __name__ == "__main__":
    sum_active_ri_by_expiry_and_type()