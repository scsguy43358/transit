import os
import json
import boto3

_REGION = os.getenv("AWS_REGION", "us-east-1")

def s3_upload_file(bucket, key, filepath):
    s3 = boto3.client("s3", region_name=_REGION)
    s3.upload_file(filepath, bucket, key)

def s3_read_json(bucket, key):
    s3 = boto3.client("s3", region_name=_REGION)
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj["Body"].read().decode("utf-8"))

def get_secret(secret_name):
    sm = boto3.client("secretsmanager", region_name=_REGION)
    r = sm.get_secret_value(SecretId=secret_name)
    if "SecretString" in r:
        return json.loads(r["SecretString"])
    return {}

def sqs_send_message(queue_url, body: dict):
    sqs = boto3.client("sqs", region_name=_REGION)
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(body))
