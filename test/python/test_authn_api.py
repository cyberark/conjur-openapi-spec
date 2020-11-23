from __future__ import absolute_import

import os
import unittest
import pathlib
import json

import openapi_client
from openapi_client.api.authn_api import AuthnApi  # noqa: E501
from openapi_client.rest import ApiException

# SSL cert constants
CERT_DIR = pathlib.Path('config/https')
SSL_CERT_FILE = 'ca.crt'
CONJUR_CERT_FILE = 'conjur.crt'
CONJUR_KEY_FILE = 'conjur.key'

# Environment Constants
CONJUR_AUTHN_API_KEY = 'CONJUR_AUTHN_API_KEY'
CONJUR_AUTHN_LOGIN = 'CONJUR_AUTHN_LOGIN'
CONJUR_ACCOUNT = 'CONJUR_ACCOUNT'

class TestAuthnApi(unittest.TestCase):
    """AuthnApi integration tests. Ensures that authentication with a Conjur server is working"""

    @classmethod
    def setUpClass(cls):
        cls.api_key = os.environ[CONJUR_AUTHN_API_KEY]
        cls.account = os.environ[CONJUR_ACCOUNT]

    @classmethod
    def tearDownClass(cls):
        # ensures that the proper API key is set for other test cases after the key rotation test
        os.environ.update({CONJUR_AUTHN_API_KEY: cls.api_key})

    def setUp(self):
        # We generate a fresh config and API instance each time to make sure
        # test runs dont interfere with eachother
        self.config = openapi_client.Configuration(
                host="https://conjur-https",
        )

        self.config.ssl_ca_cert = CERT_DIR.joinpath(SSL_CERT_FILE)
        self.config.cert_file = CERT_DIR.joinpath(CONJUR_CERT_FILE)
        self.config.key_file = CERT_DIR.joinpath(CONJUR_KEY_FILE)
        self.config.username = os.environ[CONJUR_AUTHN_LOGIN]
        self.config.password = self.api_key
        
        self.client = openapi_client.ApiClient(self.config)
        self.api = openapi_client.api.authn_api.AuthnApi(self.client)

    def tearDown(self):
        self.client.close()

    def test_authenticate(self):
        """Test case for authenticate

        Gets a short-lived access token, which can be used to authenticate requests to (most of) the rest of the Conjur API.
        """
        login = self.config.username
        body = self.api_key

        response = self.api.authenticate(self.account, login, body).replace("\'","\"")
        response_json = json.loads(response)
        response_keys = response_json.keys()
        
        self.assertIn("protected", response_keys)
        self.assertIn("payload", response_keys)
        self.assertIn("signature", response_keys)

    def test_login(self):
        """Test case for login

        Gets the API key of a user given the username and password via HTTP Basic Authentication.
        """
        # Attempt to login
        self.api.login(self.account)

        # Ensure we cannot login with a bad password
        self.config.password = "FakePassword123"

        with self.assertRaises(openapi_client.exceptions.ApiException):
            self.api.login(self.account)

    def test_rotate_api_key(self):
        """Test case for rotate_api_key

        Rotates a user’s API key.
        """
        # Rotate the key and attempt to login with it
        new_key = self.api.rotate_api_key(self.account)

        self.config.password = new_key

        self.api.login(self.account)

        # We rotated the API key so we have to update the class variable
        self.__class__.api_key = new_key

    def test_set_password(self):
        """Test case for set_password

        Changes a user’s password.
        """
        # Set a new password and try to authenticate with it
        test_password = "PAssword!234"

        response = self.api.set_password(self.account, body=test_password)
        self.config.password = test_password

        self.api.login(self.account)

        # Attempt to change password with bad auth info
        self.config.password = "BadPassword"

        with self.assertRaises(openapi_client.exceptions.ApiException):
            self.api.login(self.account)

        self.config.password = test_password

        # Attempt to set the users password to something invalid
        invalid_pass = 'SomethingInvalid'

        with self.assertRaises(openapi_client.exceptions.ApiException):
            self.api.set_password(self.account, body=invalid_pass)

if __name__ == '__main__':
    unittest.main()
