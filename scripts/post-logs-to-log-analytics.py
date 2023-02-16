#!/usr/bin/env python3

import json
import requests
import datetime
import hashlib
import hmac
import base64
import os

# Update the customer ID to your Log Analytics workspace ID & shared key
workspace_id = os.environ['WORKSPACE_ID']
workspace_key = os.environ['WORKSPACE_KEY']
payload_file_path = os.environ['PAYLOAD_FILE_PATH']
custom_log_name = os.environ['CUSTOM_LOG_NAME']
environment = os.environ['ENVIRONMENT']

# The log type is the name of the event that is being submitted
log_type = custom_log_name

# Opening JSON file 
jsonfile = open(payload_file_path,'rt') 
  
# returns JSON object as a dictionary 
json_data = json.load(jsonfile) 
body = json.dumps(json_data)

# Closing file 
jsonfile.close()


#####################
######Functions######  
#####################

# Build the API signature
def build_signature(workspace_id, workspace_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(workspace_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(workspace_id,encoded_hash)
    return authorization

# Build and send a request to the POST API
def post_data(workspace_id, workspace_key, body, log_type, environment):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(workspace_id, workspace_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + workspace_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'
    
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date,
        'environment': environment
    }

    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print ("Accepted")
    else:
        print ("Response code: {}".format(response.status_code))

post_data(workspace_id, workspace_key, body, log_type, environment)
