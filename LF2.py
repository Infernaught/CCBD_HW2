import os
import json
import string
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError

REGION = 'us-east-1'
HOST = 'search-photos-2jmjglwsrhdiu6pxozfdxexvoe.us-east-1.es.amazonaws.com'
INDEX = 'photos'

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

def query(term):
    q = {'size': 1, 'query': {'multi_match': {'query': term}}}

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    res = client.search(index=INDEX, body=q)
    #print(res)

    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_id'])

    return results

def dispatch(event):
    client = boto3.client('lexv2-runtime')

    msg_from_user = event["queryStringParameters"]['q']

    print(f"Message from frontend: {msg_from_user}")

    # Initiate conversation with Lex
    response = client.recognize_text(
            botId='QRLRNAADFW', # MODIFY HERE
            botAliasId='PIAARW6SBI', # MODIFY HERE
            localeId='en_US',
            sessionId='testuser',
            text=msg_from_user)
    
    print(f"Response from lex: {response}")
    
    
    msg_from_lex = response.get('messages', [])
    if msg_from_lex:
        labels = msg_from_lex[0]['content']
        print(f"labels interpreted: ", labels)
        labels = labels.split(',')
        if labels[0] != 'label1':
            query(labels[0])
        if labels[1] != 'label2':
            query(labels[1])
        
        resp = {
            'statusCode': 200,
            'results': [{
                'url': 'string',
                'labels': [
                    'string'
                ]
            }]
        }
        return resp

def lambda_handler(event, context):
    print(f"event: {event}")
    print(f"context: {context}")

    response = dispatch(event)
    return response