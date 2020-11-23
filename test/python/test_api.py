import json
import os
import pathlib
import unittest

import openapi_client
import openapi_client.models.access_token

CERT_DIR = pathlib.Path('config/https')
SSL_CERT_FILE = 'ca.crt'
CONJUR_CERT_FILE = 'conjur.crt'
CONJUR_KEY_FILE = 'conjur.key'

class ApiTest(unittest.TestCase):
    def setUp(self):
        self.config = openapi_client.Configuration(
                host="https://conjur-https",
                api_key={'conjurAuth': os.environ['CONJUR_AUTHN_API_KEY']}
        )
        self.config.ssl_ca_cert = CERT_DIR.joinpath(SSL_CERT_FILE)
        self.config.cert_file = CERT_DIR.joinpath(CONJUR_CERT_FILE)
        self.config.key_file = CERT_DIR.joinpath(CONJUR_KEY_FILE)

    def test_authenticate(self):
        with openapi_client.ApiClient(self.config) as api_client:
            api_instance = openapi_client.AuthnApi(api_client)
            account = os.environ['CONJUR_ACCOUNT']
            login = os.environ['CONJUR_AUTHN_LOGIN']
            body = os.environ['CONJUR_AUTHN_API_KEY']

            api_response = api_instance.authenticate(account, login, body).replace("\'","\"")
            api_response_json = json.loads(api_response)
            api_response_keys = api_response_json.keys()
            
            self.assertIn("protected", api_response_keys)
            self.assertIn("payload", api_response_keys)
            self.assertIn("signature", api_response_keys)