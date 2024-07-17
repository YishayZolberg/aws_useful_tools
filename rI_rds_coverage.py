import boto3

PAYER_PROFILE_NAME = 'example'
REGION = 'us-east-1'

rds_client = boto3.session.Session(profile_name=PAYER_PROFILE_NAME, region_name=REGION).client('rds')
results_dic = {}

response = rds_client.describe_db_instances()
rds_instances = response['DBInstances']
for instance in rds_instances:
    results_dic[instance['DBInstanceClass']] = results_dic.get(instance['DBInstanceClass'], 0) + 1
    print("Instance Identifier:", instance['DBInstanceIdentifier'])
    print("Engine:", instance['Engine'])
    print("Status:", instance['DBInstanceStatus'])
    print("Instance Class:", instance['DBInstanceClass'])
    print("Endpoint:", instance['Endpoint']['Address'])
    print("---------------------------")
print(f"Counter: {results_dic}")
