import boto3
import botocore.client


s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))
