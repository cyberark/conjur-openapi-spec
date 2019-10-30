#!/usr/bin/env python3

import sys

import swagger_client
from swagger_client.rest import ApiException

ACCOUNT_NAME = "myorg"

config = swagger_client.Configuration()
config.host = "https://localhost"

# config.debug=True

config.verify_ssl = False
config.assert_hostname = False

config.username = "admin"
config.password = "mypassword"

login_api = swagger_client.AuthnApi(swagger_client.ApiClient(config))

api_key = None
try:
    api_key = login_api.login(account=ACCOUNT_NAME)
except ApiException as err:
    print("Exception when logging in: ", err)
    sys.exit(1)

print("API key:", api_key)

authn_api = swagger_client.AuthnApi(swagger_client.ApiClient(config))
try:
    conjur_access_token = authn_api.authenticate(api_key, account=ACCOUNT_NAME, login="admin")
    print(conjur_access_token)
except ApiException as err:
    print("Exception when authenticating in: ", err)
    sys.exit(1)

try:
    login_api.set_password("mypassword", account=ACCOUNT_NAME)
except ApiException as err:
    print("Exception when setting password in: ", err)
    sys.exit(1)

try:
    api_key = login_api.rotate_api_key(account=ACCOUNT_NAME)
except ApiException as err:
    print("Exception when logging in: ", err)
    sys.exit(1)

print("New API key:", api_key)

#encoded_token = base64.b64encode(conjur_access_token.to_str().encode()).decode('utf-8')
#config.api_key['authorization'] = "token=\"%s\"".format(encoded_token)
#config.api_key_prefix['authorization'] = 'Token'

print("Done!")
