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

def getJobStatus(job_id):
    response = textract_client.get_document_text_detection(JobId=job_id)
    status = response["JobStatus"]
    print(f"Job status: {status}")
    return status

def getJobResults(job_id):

    pages = []

    response = textract_client.get_document_text_detection(JobId=job_id)

    pages.append(response)
    print("Resultset page recieved: {}".format(len(pages)))
    nextToken = None
    if('NextToken' in response):
        nextToken = response['NextToken']

    while(nextToken):
        time.sleep(5)

        response = textract_client.get_document_text_detection(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        print("Resultset page recieved: {}".format(len(pages)))
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']

    return pages

def lambda_handler(event, context):
    job_id = event['job_id']

    input_bucket = event['bucket_name']
    input_object = event['object_name']

    output_bucket = os.getenv('OUTPUT_BUCKET', input_bucket)
    output_prefix = os.environ['OUTPUT_PREFIX']

    output_object = os.path.join(output_prefix, os.path.basename(input_object))
    print(f"s3://{input_bucket}/{input_object} -> s3://{output_bucket}/{output_object}")

    event['job_status'] = getJobStatus(job_id)
    event['job_update_timestamp'] = time.time()

    return event
    #if(isJobComplete(jobId)):
    #    response = getJobResults(jobId)

    #for resultPage in response:
    #    for item in resultPage["Blocks"]:
    #        if item["BlockType"] == "LINE":
    #            print ('\033[94m' +  item["Text"] + '\033[0m')

    #return {
    #    "input": f"s3://{input_bucket}/{input_object}",
    #    "output": f"s3://{output_bucket}/{output_object}",
    #}

if __name__ == "__main__":
    with open(sys.argv[1], "rt") as f:
        event = json.load(f)
    ret = lambda_handler(event, {})
    print("lambda_handler(): ", json.dumps(ret))
