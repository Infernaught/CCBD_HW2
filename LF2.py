import os
import json
import string
import boto3
import inflect
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError

REGION = 'us-east-1'
HOST = 'search-photos-2jmjglwsrhdiu6pxozfdxexvoe.us-east-1.es.amazonaws.com'
INDEX = 'photos'
from requests_aws4auth import AWS4Auth

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

def query(term):
    q = { "size": 3,
        "query": {
            "bool": {
            "must": {
                "match": {
                "labels": term
                }
            }
            }
        }
    }

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
        img = {}
        img['url'] = 'https://' + hit['_source']['bucket'] + '.s3.amazonaws.com/' + hit['_source']['objectKey']
        img['labels'] = hit['_source']['labels']
        results.append(img)

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
        p = inflect.engine()
        labels = msg_from_lex[0]['content']
        print(f"labels interpreted: ", labels)
        labels = labels.split(', ')
        img1 = img2 = []
        if labels[0] != 'label1':
            img1 = query(string.capwords(p.singluar_noun(labels[0])))
        if labels[1] != 'label2':
            img2 = query(string.capwords(p.singluar_noun(labels[1])))
        else:
            labels = [labels[0]]
        label = [{'url':None, 'labels': labels}]
        json_resp = {'results': label + img1 + img2}
        resp = {
            "isBase64Encoded": False,
            'statusCode': 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps(json_resp)
        }
        print(resp)
        return resp
    else:
        json_resp = {'results': label}
        resp = {
            "isBase64Encoded": False,
            'statusCode': 403,
            "headers": {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps(json_resp)
        }
        print(resp)
        return resp

def lambda_handler(event, context):
    print(f"event: {event}")
    print(f"context: {context}")

    response = dispatch(event)
    return response