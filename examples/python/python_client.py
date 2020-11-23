#!/usr/bin/env python3

import base64
import os
import pathlib
import sys

import openapi_client
from openapi_client.rest import ApiException

CERT_DIR = pathlib.Path('config/https')
SSL_CERT_FILE = 'ca.crt'
CONJUR_CERT_FILE = 'conjur.crt'
CONJUR_KEY_FILE = 'conjur.key'

ACCOUNT_NAME = "dev"
LOGIN = "admin"
ADMIN_API_KEY = os.environ["CONJUR_ADMIN_API_KEY"]

# Setup API client config
config = openapi_client.Configuration()
config.host = "http://localhost"
# config.debug = True
config.verify_ssl = True
config.username = LOGIN
config.password = ADMIN_API_KEY
config.ssl_ca_cert = CERT_DIR.joinpath(SSL_CERT_FILE)
config.cert_file = CERT_DIR.joinpath(CONJUR_CERT_FILE)
config.key_file = CERT_DIR.joinpath(CONJUR_KEY_FILE)

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

# Add Conjur Token header to client configuration
token_body = 'token="{}"'.format(access_token)
api_client.configuration.api_key = {'Authorization': token_body}
api_client.configuration.api_key_prefix = {'Authorization': 'Token'}

policy_api = openapi_client.PoliciesApi(api_client)
login_api = openapi_client.AuthnApi(api_client)

# Load empty policy, allows the example to be run multiple times sequentially
# Loading a policy returns data for users CREATED when the policy is loaded. Without loading 
# an "empty" policy, if the user alice already exists due to a prior example run, loading 
# the full policy will not respond with alice's api key.
print("\nLoading empty root policy...")
empty_policy = "- !user admin"
empty_results = None
try:
    empty_results = policy_api.load_policy(account=ACCOUNT_NAME, identifier="root", body=empty_policy)
    print("Empty policy loaded.")
except ApiException as err:
    print("Exception when loading empty policy: ", err)
    sys.exit(1)

# Load a policy using api client
print("\nLoading root policy...")
policy = """---
- !user admin
- !user alice
- !variable sampleSecret

- !permit
  role: !user admin
  privilege: [ update ]
  resource: !user alice

- !permit
  role: !user admin
  privilege: [ execute ]
  resource: !variable sampleSecret
"""
loaded_results = None
try:
    loaded_results = policy_api.load_policy(account=ACCOUNT_NAME, identifier="root", body=policy)
    print("Policy loaded.")
except ApiException as err:
    print("Exception when loading policy: ", err)
    sys.exit(1)
alice_api_key = loaded_results["created_roles"]["dev:user:alice"]["api_key"]
print("Alice API key: ", alice_api_key)

# Rotate Alice's API key, uses conjurAuth
print("\nRotating alice API key...")
try:
    ADMIN_API_KEY = login_api.rotate_api_key(account=ACCOUNT_NAME, role="user:alice")
    print("New API key:", ADMIN_API_KEY)
except ApiException as err:
    print("Exception when logging in: ", err)
    sys.exit(1)

# Store a secret, uses conjurAuth
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

# Retrieve secrets, uses conjurAuth
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
