#!/usr/bin/env python3

import base64
import os
import sys

import openapi_client
from openapi_client.rest import ApiException

ACCOUNT_NAME = "dev"
LOGIN = "admin"
ADMIN_API_KEY = os.environ["CONJUR_ADMIN_API_KEY"]

# Setup API client config
config = openapi_client.Configuration()
config.host = "http://conjur-https"
# config.debug = True
config.verify_ssl = True
config.username = LOGIN
config.password = ADMIN_API_KEY

api_client = openapi_client.ApiClient(config)
login_api = openapi_client.AuthnApi(api_client)

# Authenticate admin using basicAuth, receiving short-lived access token
print("Authenticating admin...")
access_token = None
try:
    access_token = login_api.authenticate(account=ACCOUNT_NAME, login=LOGIN, body=ADMIN_API_KEY, accept_encoding="base64")
    print("Base64 encoded token:", access_token)
except ApiException as err:
    print("Exception when authenticating in: ", err)
    sys.exit(1)

# Change admin password, uses basicAuth
print("\nChanging admin password...")
new_password = "N3w-Passw0rd!"
try:
    login_api.set_password(body=new_password, account=ACCOUNT_NAME)
    print("Password change successful.")
except ApiException as err:
    print("Exception when setting password in: ", err)
    sys.exit(1)
api_client.configuration.password = new_password

# Rotate admin API key, uses basicAuth
print("\nRotating admin API key...")
try:
    ADMIN_API_KEY = login_api.rotate_api_key(account=ACCOUNT_NAME)
    print("New API key:", ADMIN_API_KEY)
except ApiException as err:
    print("Exception when logging in: ", err)
    sys.exit(1)

# Add Conjur Token header to client configuration
token_body = 'token="{}"'.format(access_token)
api_client.configuration.api_key = {'conjurAuth': token_body}
api_client.configuration.api_key_prefix = {'conjurAuth': 'Token'}

policy_api = openapi_client.PoliciesApi(api_client)

# Load a policy using api client
print("\nLoading root policy...")
policy = """---
- !variable
  id: sampleSecret

- !permit
  role: !user admin
  privilege: [ execute ]
  resource: !variable sampleSecret
"""
try:
    policy_api.load_policy(account=ACCOUNT_NAME, identifier="root", body=policy)
    print("Policy loaded.")
except ApiException as err:
    print("Exception when loading policy: ", err)
    sys.exit(1)

# Store a secret
print("\nStoring secret...")
secrets_api = openapi_client.SecretsApi(api_client)
secret = "supersecretstuff"
secret_id = "sampleSecret"
print("Secret data: ", secret)
try:
    secrets_api.create_variable(account=ACCOUNT_NAME, kind="variable", identifier=secret_id, body=secret)
    print("Secret stored.")
except ApiException as err:
    print("Exception when creating secret: ", err)
    sys.exit(1)

# Retrieve secrets
print("\nRetrieving secret...")
retrieved_secret = None
try:
    retrieved_secret = secrets_api.get_variable(account=ACCOUNT_NAME, kind="variable", identifier=secret_id)
    print("Retrieved seceret: ", retrieved_secret)
except ApiException as err:
    print("Exception when retrieving secret: ", err)
    sys.exit(1)

if retrieved_secret != secret:
    print("Secret Malformed.")
    print("Secret stored: ", secret)
    print("Secret retrieved: ", retrieved)
    sys.exit(1)

print("\nDone!")
