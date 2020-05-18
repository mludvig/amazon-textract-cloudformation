#!/usr/bin/env python3

import json
import time
import boto3

textract_client = boto3.client('textract')

def startJob(bucket_name, object_name):
    response = textract_client.start_document_analysis(
        DocumentLocation={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': object_name,
            }
        },
        FeatureTypes=['TABLES', 'FORMS'],
    )

    return response["JobId"]

def lambda_handler(event, context):
    if event.get('source') != 'aws.s3':
        print("ERROR: Unexpected event type")
        print(json.dumps(event))
        raise ValueError("ERROR: Unexpected event type")

    bucket_name = event['detail']['requestParameters']['bucketName']
    object_name = event['detail']['requestParameters']['key']

    print(f"StartJob: s3://{bucket_name}/{object_name}")

    job_id = startJob(bucket_name, object_name)
    print(f"JobId: {job_id}")

    return {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "job_id": job_id,
        "job_start_timestamp": time.time(),
    }

if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "rt") as f:
        event = json.load(f)
    ret = lambda_handler(event, {})
    print(json.dumps(ret, indent=2))
