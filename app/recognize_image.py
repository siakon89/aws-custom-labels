import boto3
import json
import os
from authorizer import is_authorized


BUCKET_NAME = os.environ.get("IMAGE_BUCKET")
MODEL_ARN = os.environ.get("MODEL_ARN")


def show_custom_labels(model,bucket,photo, min_confidence):

    session = boto3.session.Session(region_name='us-west-2')
    
    client = session.client('rekognition')

    # Call DetectCustomLabels
    response = client.detect_custom_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model
    )
    
    return response


def lambda_handler(event, context):
    
    if not is_authorized(event.get("headers", {})):
        return {
            "body": json.dumps({"message": "Invalid API key"}),
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        }

    image_name = event["queryStringParameters"].get("image_name")
    min_confidence = event["queryStringParameters"].get("min_confidence", 80)

    try:
        response = show_custom_labels(MODEL_ARN, BUCKET_NAME, os.path.join('images', image_name), min_confidence)
    
        return {
            "statusCode": 200,
            "body": json.dumps({"response": response}),
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"response": str(e)}),
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        }
