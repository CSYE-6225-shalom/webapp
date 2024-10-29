import boto3
import os
from botocore.exceptions import ClientError
import logging

# Initialize the S3 client using the default credential provider chain
s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))


def upload_to_s3(file, bucket_name, object_name):
    logging.info("Starting upload to S3")
    try:
        response = s3_client.upload_fileobj(file, bucket_name, object_name)
        return response
    except ClientError as e:
        logging.error(e)
        return None


def delete_from_s3(bucket_name, object_name):
    logging.info("Starting deletion from S3")
    try:
        response = s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        return response
    except ClientError as e:
        logging.error(e)
        return None
