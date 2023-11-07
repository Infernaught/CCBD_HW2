import json
import boto3
from datetime import datetime

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

REGION = "us-east-1"
HOST = "search-photos-2jmjglwsrhdiu6pxozfdxexvoe.us-east-1.es.amazonaws.com"
INDEX = "photos"

def getawsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key, cred.secret_key, region, service, session_token=cred.token)

def add_to_os(mapping):
    client = OpenSearch(hosts=[{"host":HOST,"port":443}],
        http_auth=getawsauth(REGION, "es"),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    #try:
    #    res = client.indices.create(index=INDEX)
    #except:
    #    pass
    response = client.index(index=INDEX, body=mapping)
        
    return response

def lambda_handler(event, context):
    rclient = boto3.client('rekognition', REGION)
    info = event["Records"][0]
    bucket = info["s3"]["bucket"]["name"]
    obj = info["s3"]["object"]["key"]
    print(f"Bucket: {bucket}; Object: {obj}")
    if info["eventSource"] == "aws:s3" and info["eventName"] == "ObjectCreated:Put":
        rresponse = rclient.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':obj}})
    s3client = boto3.client("s3", REGION)
    s3response = s3client.head_object(Bucket=bucket, Key=obj)
    labels = []
    if "x-amz-meta-customLabels" in s3response:
        labels += s3response["x-amz-meta-customLabels"]
    for label in rresponse["Labels"]:
        labels.append(label["Name"])
    curr_time = datetime.now().strftime("%Y-%m-$dT%H:%M:%S")
    json_dict = {"objectKey": obj, "bucket": bucket, "createdTimestamp": curr_time, "labels": labels}
    response = add_to_os(json_dict)
    print(f'response: {response}')
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }