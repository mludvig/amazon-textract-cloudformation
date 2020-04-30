#!/usr/bin/env python3

import os
import json
import boto3

textract_client = boto3.client('textract')

def startJob(bucket_name, object_name):
    response = textract_client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': object_name,
            }
        }
    )

    return response["JobId"]

def lambda_handler(event, context):
    if event.get('source') != 'aws.s3' or event['detail']['eventName'] != 'PutObject':
        print("ERROR: Unexpected event type")
        print(json.dumps(event))
        return False

    bucket_name = event['detail']['requestParameters']['bucketName']
    object_name = event['detail']['requestParameters']['key']

    print(f"StartJob: s3://{bucket_name}/{object_name}")

    job_id = startJob(bucket_name, object_name)
    print(f"JobId: {job_id}")

    return {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "job_id": job_id,
    }

if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "rt") as f:
        event = json.load(f)
    ret = lambda_handler(event, {})
    print(json.dumps(ret, indent=2))
