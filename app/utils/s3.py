import boto3
import os
from botocore.exceptions import ClientError

# Initialize the S3 client using the default credential provider chain
s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))


def upload_to_s3(file, bucket_name, object_name):
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        return True
    except ClientError as e:
        print(e)
        return False


def delete_from_s3(bucket_name, object_name):
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        return True
    except ClientError as e:
        print(e)
        return False
