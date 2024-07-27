# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose
Test code for running the Amazon Textract Lambda
function example code.
"""

import argparse
import logging
import base64
import json
import io
import boto3
import uuid

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    
    
    
    # get the type of request and call handler
    
    # image = open('test.jpg', 'rb')
    # image_read = image.read()
    
    
    req = event["requestContext"]['http']['method']
    
    # imageBody = base64.b64decode(event['body'])
    # print(event)
    body = event['body']
    # image_bytes = body['image'].encode('utf-8')
    # img_b64dec = base64.b64decode(image_bytes)
    # img_byteIO = BytesIO(img_b64dec)
    # image = Image.open(img_byteIO)
    # body[''] = image
    
    # extract caller information
    caller_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    
    if req == "POST":
        return handle_post(body, caller_id)
        
def upload_image_to_s3(data):
    print("Print in Upload")
    
    print(data)
    print(type(data))
    
    
    bucket = 'soulscribejournalimages'
    s3 = boto3.client('s3')
    s3_file_name = f"{str(uuid.uuid4())}.jpg"
    try:
        s3.put_object(Bucket=bucket, Key=s3_file_name, Body=data)
        print("File Successfully Uploaded")
    except ClientError:
        print("Couldn't put object to bucket.")
        
    url = f"s3://{bucket}/{s3_file_name}"
    
    return url
    
    
def analyze_image(function_name, image):
    """Analyzes a document with an AWS Lambda function.
    :param image: The document that you want to analyze.
    :return The list of Block objects in JSON format.
    """

    lambda_client = boto3.client('lambda')

    lambda_payload = {}

    if image.startswith('s3://'):
        logger.info("Analyzing document from S3 bucket: %s", image)
        bucket, key = image.replace("s3://", "").split("/", 1)
        s3_object = {
            'Bucket': bucket,
            'Name': key
        }

        lambda_payload = {"S3Object": s3_object}

    else:
        with open(image, 'rb') as image_file:
            logger.info("Analyzing local document: %s ", image)
            image_bytes = image_file.read()
            data = base64.b64encode(image_bytes).decode("utf8")

            lambda_payload = {"image": data}

    # Call the lambda function with the document.

    response = lambda_client.invoke(FunctionName=function_name,
                                    Payload=json.dumps(lambda_payload))

    return json.loads(response['Payload'].read().decode())



def handle_post(data, caller_id):
    data = json.loads(data)
    
    data['JournalImageString'] = base64.b64decode(data['JournalImageString'])
    
    url = upload_image_to_s3(data['JournalImageString'])
    
    function_name = 'journal-upload'
    
    # Get analysis results.
    result = analyze_image(function_name, url)
    status = result['statusCode']

    blocks = result['body']
    print(blocks)
    blocks = json.loads(blocks)
    
    journal_entry = []
    journal_string = ""
    
    if status == 200:

        for block in blocks:
            print('Type: ' + block['BlockType'])
            
            if block['BlockType'] == "LINE":
                journal_string += block['Text']
                
                journal_string += ' '
            
            
            # if block['BlockType'] != 'PAGE':
            # if block['BlockType'] == 'WORD':
            #     journal_entry.append(block['Text'])
                
        #         print('Detected: ' + block['Text'])
        #         print('Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")

        #     print('Id: {}'.format(block['Id']))
        #     if 'Relationships' in block:
        #         print('Relationships: {}'.format(block['Relationships']))
        #     print('Bounding Box: {}'.format(block['Geometry']['BoundingBox']))
        #     print('Polygon: {}'.format(block['Geometry']['Polygon']))
        #     print()
        # print("Blocks detected: " + str(len(blocks)))
        
        # format the request to be a path request
        
        # data_patch = data.copy()
        # function_name = 'journals-journal'
        # data_patch["requestContext"]['http']['method'] = "PATCH"
        # data_patch['CurrentStageData'] = str(journal_entry)
        
        # response = lambda_client.invoke(FunctionName=function_name,
        #                         Payload=json.dumps(data_patch))
        
    else:
        print(f"Error: {result['statusCode']}")
        print(f"Message: {result['body']}")
        
    response = {'user_id': caller_id, 'journal_entry': journal_string}
    
    return response
    

