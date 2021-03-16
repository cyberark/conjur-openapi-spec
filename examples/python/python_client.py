#!/usr/bin/env python3

import base64
import os
import pathlib
import sys

import conjur
from conjur.rest import ApiException

CERT_DIR = pathlib.Path('config/https')
SSL_CERT_FILE = 'ca.crt'
CONJUR_CERT_FILE = 'conjur.crt'
CONJUR_KEY_FILE = 'conjur.key'

ACCOUNT_NAME = "dev"
LOGIN = "admin"
ADMIN_API_KEY = os.environ["CONJUR_ADMIN_API_KEY"]

# Constants
new_password = "N3w-Passw0rd!"
secret = "supersecretstuff"
secret_id = "sampleSecret"
simple_policy = None
with open("config/policy/simple.yml", "r") as file:
    empty_policy = file.read()
policy = None
with open("config/policy/policy.yml", "r") as file:
    policy = file.read()

# Setup API client config
config = conjur.Configuration()
config.host = "https://conjur-https"
# config.debug = True
config.verify_ssl = True
config.username = LOGIN
config.password = ADMIN_API_KEY
config.ssl_ca_cert = CERT_DIR.joinpath(SSL_CERT_FILE)
config.cert_file = CERT_DIR.joinpath(CONJUR_CERT_FILE)
config.key_file = CERT_DIR.joinpath(CONJUR_KEY_FILE)

api_client = conjur.ApiClient(config)
login_api = conjur.AuthenticationApi(api_client)

# Authenticate admin using basicAuth, receiving short-lived access token
print("Authenticating admin...")

access_token = login_api.get_access_token(
    account=ACCOUNT_NAME,
    login=LOGIN,
    body=ADMIN_API_KEY,
    accept_encoding="base64"
)
print("Base64 encoded token:", access_token)

# Change admin password, uses basicAuth
print("\nChanging admin password...")
login_api.change_password(
    body=new_password,
    account=ACCOUNT_NAME
)
print("Password change successful.")

api_client.configuration.password = new_password

# Add Conjur Token header to client configuration
token_body = 'token="{}"'.format(access_token)
api_client.configuration.api_key = {'Authorization': token_body}
api_client.configuration.api_key_prefix = {'Authorization': 'Token'}

policy_api = conjur.PoliciesApi(api_client)
login_api = conjur.AuthenticationApi(api_client)

# Load simple policy, which only defines an admin user
# Allows the example to be run multiple times sequentially
# Loading a policy returns data for users CREATED when the policy is loaded. Without loading
# the simple policy, if the user alice already exists due to a prior example run, loading
# the full policy will not respond with alice's api key.
print("\nLoading simple root policy...")
policy_api.replace_policy(
    ACCOUNT_NAME,
    "root",
    empty_policy
)
print("Empty policy loaded.")

# Load a policy using api client
print("\nLoading root policy...")
loaded_results = policy_api.replace_policy(
    ACCOUNT_NAME,
    "root",
    body=policy
)
print("Policy loaded.")

alice_api_key = loaded_results.created_roles["dev:user:alice"]["api_key"]
print("Alice API key: ", alice_api_key)

# Rotate Alice's API key, uses conjurAuth
print("\nRotating alice API key...")
alice_api_key = login_api.rotate_api_key(
    ACCOUNT_NAME,
    role="user:alice"
)
print("New API key:", alice_api_key)

# Store a secret, uses conjurAuth
print("\nStoring secret...")
secrets_api = conjur.SecretsApi(api_client)
print("Secret data: ", secret)
secrets_api.create_secret(
    ACCOUNT_NAME,
    "variable",
    secret_id,
    body=secret
)
print("Secret stored.")

# Retrieve secrets, uses conjurAuth
print("\nRetrieving secret...")
retrieved_secret = secrets_api.get_secret(
    ACCOUNT_NAME,
    "variable",
    secret_id
)
print("Retrieved seceret: ", retrieved_secret)

if retrieved_secret != secret:
    print("Secret Malformed.")
    print("Secret stored: ", secret)
    print("Secret retrieved: ", retrieved)
    sys.exit(1)

print("\nDone!")
