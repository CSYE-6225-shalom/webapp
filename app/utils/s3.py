import boto3
import os
from botocore.exceptions import ClientError
from statsd import StatsClient
import time
from functools import wraps


aws_access_key_id = os.getenv("S3_AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("S3_AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")

# Initialize an S3 client with the credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# # Initialize the S3 client using the default credential provider chain
# s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))

# Initialize StatsD client
statsd_client = StatsClient()


# Decorators to measure the number of calls, duration, and package size of S3 operations
def measure_s3_call_count(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        endpoint = func.__name__
        statsd_client.incr(f's3.{endpoint}.calls')
        return func(*args, **kwargs)
    return wrapper


def measure_s3_call_duration(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        endpoint = func.__name__
        statsd_client.timing(f's3.{endpoint}.duration', duration * 1000)  # in ms
        return result
    return wrapper


def measure_s3_package_size(func):
    @wraps(func)
    def wrapper(file, bucket_name, object_name):
        file.seek(0, os.SEEK_END)  # Move the cursor to the end of the file
        file_size = file.tell()  # Get the current position of the cursor, which is the size of the file
        file.seek(0)  # Reset the cursor to the beginning of the file
        endpoint = func.__name__
        statsd_client.gauge(f's3.{endpoint}.package_size', file_size)  # Send the file size to StatsD
        return func(file, bucket_name, object_name)
    return wrapper

@measure_s3_call_count
@measure_s3_call_duration
@measure_s3_package_size
def upload_to_s3(file, bucket_name, object_name):
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        return True
    except ClientError as e:
        print(e)
        return False

@measure_s3_call_count
@measure_s3_call_duration
def delete_from_s3(bucket_name, object_name):
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        return True
    except ClientError as e:
        print(e)
        return False
