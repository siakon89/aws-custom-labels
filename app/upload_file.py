import json
import os
import boto3
from botocore.exceptions import ClientError
from authorizer import is_authorized


BUCKET_NAME = os.environ.get("IMAGE_BUCKET")


def lambda_handler(event, context):
    
    if not is_authorized(event.get("headers", {})):
        return {
            "body": json.dumps({"message": "Invalid API key"}),
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        }
    
    if "image_name" not in event["queryStringParameters"]:
        return {
            "body": json.dumps({"message": "Missing required parameter: image_name"}),
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        }
    image_name = event["queryStringParameters"].get("image_name")

    prefix = f"images/{image_name}"

    s3_client = boto3.client("s3")
    try:
        response = s3_client.generate_presigned_post(
            BUCKET_NAME,
            prefix,
            Conditions=[["content-length-range", 1, 100_000_000]],
            ExpiresIn=3600,
        )
    except ClientError as e:
        return {
            "body": json.dumps({"message": str(e)}),
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        }

    if "url" not in response:
        return {
            "body": json.dumps({"message": "No url generated, contact admin."}),
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"response": response}),
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
    }
