#!/usr/bin/env python3

import sys
import time
import base64
import openapi_client
from openapi_client.rest import ApiException

def format_and_encode (token):
    reordered_token='{"protected":"'
    reordered_token=reordered_token+token.protected
    reordered_token=reordered_token+'","payload":"'
    reordered_token=reordered_token+token.payload
    reordered_token=reordered_token+'","signature":"'
    reordered_token=reordered_token+token.signature
    reordered_token=reordered_token+'"}'
    
    compressed_token = reordered_token.replace("\n","").replace("\r","").replace(" ","")
    encoded_token = base64.b64encode(compressed_token.encode()).decode('utf-8')
    
    return encoded_token

ACCOUNT_NAME = "cucumber"

# setup API client config
config = openapi_client.Configuration()
config.host = "http://localhost:3000"
config.debug=True
config.verify_ssl = False
# config.assert_hostname = False
config.username = "admin"
config.password = "My-Passw0rd!"


# new api client
api_client = openapi_client.ApiClient(config)
# authentication client
login_api = openapi_client.AuthnApi(api_client)

# login as admin, receiving admin API key in response
api_key = None
try:
    api_key = login_api.login(account=ACCOUNT_NAME)
    print("API key:", api_key)
except ApiException as err:
    print("Exception when logging in: ", err)
    sys.exit(1)
    
# authenticate admin, receiving short-lived access token
access_token = None
try:
    access_token = login_api.authenticate(account=ACCOUNT_NAME, login="admin", body=api_key)
    print(access_token)
except ApiException as err:
    print("Exception when authenticating in: ", err)
encoded_token = format_and_encode(access_token)

# change admin password using basicAuth
new_password = "N3w-Passw0rd!"
try:
    login_api.set_password(body=new_password, account=ACCOUNT_NAME)
except ApiException as err:
    print("Exception when setting password in: ", err)
    sys.exit(1)
print("Password change successful.")
api_client.configuration.password = new_password

# rotate admin API key
try:
    api_key = login_api.rotate_api_key(account=ACCOUNT_NAME)
except ApiException as err:
    print("Exception when logging in: ", err)
    sys.exit(1)
print("New API key:", api_key)

# add Conjur Token header to client configuration
token_body = 'token="{}"'.format(encoded_token)
api_client.configuration.api_key = {'conjurAuth': token_body}
api_client.configuration.api_key_prefix = {'conjurAuth': 'Token'}

# restore debug flag? stops printing request logs
api_client.configuration.debug=True
# store a secret
secrets_api = openapi_client.SecretsApi(api_client)
secret = "supersecretstuff"
secret_id = "sampleSecret"
try:
    secrets_api.create_variable(account=ACCOUNT_NAME, kind="variable", identifier=secret_id, body=secret)
except ApiException as err:
    print("Exception when creating secret: ", err)
    sys.exit(1)
print("Secret stored.")

# retrieve secrets
retrieved = None
try:
    retrieved = secrets_api.get_variable(account=ACCOUNT_NAME, kind="variable", identifier=secret_id)
except ApiException as err:
    print("Exception when retrieving secret: ", err)
    sys.exit(1)
if retrieved == secret:
    print("Secret Retrieved!")
else:
    print("Secret Malformed.")
    print("Secret stored: ", secret)
    print("Secret retrieved: ", retrieved)

print("Done!")
