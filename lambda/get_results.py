#!/usr/bin/env python3

import os
import json
import time
import boto3

s3_client = boto3.client('s3')
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
    print(f"JobID: {response['JobId']}")

    return response["JobId"]

def getJobResults(job_id, next_token = None):
    kwargs = {}
    if next_token:
        kwargs['NextToken'] = next_token

    response = textract_client.get_document_analysis(JobId=job_id, **kwargs)

    return response

def lambda_handler(event, context):
    job_id = event['job_id']

    results = getJobResults(job_id)
    event['job_status'] = results['JobStatus']
    event['job_update_timestamp'] = time.time()

    if event['job_status'] != "SUCCEEDED":
        # Include the results unless the job is still in progress
        # Useful for investigating failures
        if event['job_status'] != "IN_PROGRESS":
            event['results'] = results
        return event

    # Job succeeded - retrieve the results

    input_bucket = event['bucket_name']
    input_object = event['object_name']

    output_bucket = os.getenv('OUTPUT_BUCKET', input_bucket)
    output_prefix = os.environ['OUTPUT_PREFIX']

    output_object_base = os.path.join(output_prefix, os.path.basename(input_object))

    event['raw_bucket'] = output_bucket
    event['raw_objects'] = []
    page_counter = 0
    while True:
        page_counter += 1
        output_object = f"{output_object_base}.raw.{page_counter:02d}.json"
        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_object,
            Body=json.dumps(results),
            ServerSideEncryption='AES256',
            ContentType='application/json',
        )
        event['raw_objects'].append(output_object)
        print(f"Page {page_counter:02} saved to: s3://{output_bucket}/{output_object}")

        if 'NextToken' not in results:
            break

        print(f"NextToken: {results['NextToken']}")
        results = getJobResults(job_id, next_token=results['NextToken'])

    return event

if __name__ == "__main__":
    event = {
        "bucket_name": "s3-step-bucket-1tjhxv88nuo0p",
        "object_name": "upload/template-1588283708.yml",
        "job_id": "54625eb1fb8e44c3f3877e704e6ea4483497890c6ff4cb5e7435250b77f921bf",
        "job_start_timestamp": 1588283713.1570575
    }
    ret = lambda_handler(event, {})
    print("lambda_handler(): ", json.dumps(ret))
