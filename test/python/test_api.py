import unittest
import pathlib
import os

import openapi_client
import openapi_client.models.access_token

CERT_PATH = 'test/config/https'
SSL_CERT_FILE = 'ca.crt'
CONJUR_CERT_FILE = 'conjur.crt'
CONJUR_KEY_FILE = 'conjur.key'

class ApiTest(unittest.TestCase):
    """Unittest TestCase for the Conjur Python API client against basic API endpoints"""
    def setUp(self):
        """Method run before the test case starts"""
        self.config = openapi_client.Configuration(
                host="https://conjur-https",
                api_key={'conjurAuth': os.environ['CONJUR_AUTHN_API_KEY']}
        )
        cert_path = pathlib.Path(CERT_PATH)
        self.config.ssl_ca_cert = cert_path.joinpath(SSL_CERT_FILE)
        self.config.cert_file = cert_path.joinpath(CONJUR_CERT_FILE)
        self.config.key_file = cert_path.joinpath(CONJUR_KEY_FILE)

    def test_authenticate(self):
        """Test authentication with conjur"""
        with openapi_client.ApiClient(self.config) as api_client:
            api_instance = openapi_client.AuthnApi(api_client)
            account = os.environ['CONJUR_ACCOUNT']
            login = os.environ['CONJUR_AUTHN_LOGIN']
            body = os.environ['CONJUR_AUTHN_API_KEY']

            api_response = api_instance.authenticate(account, login, body)
            self.assertIsInstance(api_response, openapi_client.models.access_token.AccessToken)
