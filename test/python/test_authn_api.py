from __future__ import absolute_import

import os
import unittest
import json

import openapi_client

from . import api_config
from .api_config import CONJUR_AUTHN_API_KEY

class TestAuthnApi(api_config.ConfiguredTest):
    """AuthnApi integration tests. Ensures that authentication with a Conjur server is working"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api_key = os.environ[CONJUR_AUTHN_API_KEY]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # ensures that the proper API key is set for other test cases after the key rotation test
        os.environ.update({CONJUR_AUTHN_API_KEY: cls.api_key})

    def setUp(self):
        # Reset the config password for each run because we change it in some tests
        self.config = api_config.get_api_config()
        self.config.password = self.api_key

        self.client = openapi_client.ApiClient(self.config)
        self.api = openapi_client.api.authn_api.AuthnApi(self.client)

        self.bad_auth_api = openapi_client.api.authn_api.AuthnApi(self.bad_auth_client)

    def tearDown(self):
        self.client.close()

    def test_authenticate(self):
        """Test case for authenticate

        Gets a short-lived access token, which can be used to authenticate requests
        to (most of) the rest of the Conjur API.
        """
        login = self.config.username
        body = self.api_key

        response = self.api.authenticate('authn', self.account, login, body).replace("\'","\"")
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
        self.api.login('authn', self.account)

        # Ensure we cannot login with a bad password
        self.config.password = "FakePassword123"

        with self.assertRaises(openapi_client.exceptions.ApiException):
            self.api.login('authn', self.account)

    def test_rotate_api_key(self):
        """Test case for rotate_api_key

        Rotates a user’s API key.
        """
        # Rotate the key and attempt to login with it
        new_key = self.api.rotate_api_key('authn', self.account)

        self.config.password = new_key

        self.api.login('authn', self.account)

        # We rotated the API key so we have to update the class variable
        self.__class__.api_key = new_key

    def test_set_password(self):
        """Test case for set_password

        Changes a user’s password.
        """ # Set a new password and try to authenticate with it
        test_password = "PAssword!234"

        self.api.set_password(self.account, body=test_password)
        self.config.password = test_password

        self.api.login('authn', self.account)

        # Attempt to change password with bad auth info
        self.config.password = "BadPassword"

        with self.assertRaises(openapi_client.exceptions.ApiException):
            self.api.login('authn', self.account)

        self.config.password = test_password

        # Attempt to set the users password to something invalid
        invalid_pass = 'SomethingInvalid'

        with self.assertRaises(openapi_client.exceptions.ApiException):
            self.api.set_password(self.account, body=invalid_pass)


class TestExternalAuthnApi(api_config.ConfiguredTest):
    """Class tests api functions relating to external authenticators

    Separate from the Authn tests to avoid issues with changing api keys/paswords
    """
    def setUp(self):
        self.api = openapi_client.api.authn_api.AuthnApi(self.client)
        self.bad_auth_api = openapi_client.api.authn_api.AuthnApi(self.bad_auth_client)

    def test_update_authenticator_config_204(self):
        """Test case for update_authenticator_config 204 response

        Updates the authenticators configuration
        """
        _, status, _ = self.api.update_authenticator_config_with_http_info(
            'authn-ldap',
            'test',
            self.account,
            enabled=True
        )

        self.assertEqual(status, 204)

    def test_update_authenticator_config_401(self):
        """Test case for update_authenticator_config 401 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.bad_auth_api.update_authenticator_config(
                'oidc',
                'okta',
                self.account,
                enabled=False
            )

        self.assertEqual(context.exception.status, 401)

    def test_update_authenticator_config_404(self):
        """Test case for update_authenticator_config 404 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.update_authenticator_config(
                'oidc',
                'okta',
                self.account,
                enabled=False
            )

        self.assertEqual(context.exception.status, 404)

    def test_service_login_200(self):
        """Test case for service_login 200 response

        Login with the given authenticator
        """
        alice_config = api_config.get_api_config(username='alice')
        alice_config.password = 'alice'
        alice_client = openapi_client.ApiClient(alice_config)
        alice_api = openapi_client.api.authn_api.AuthnApi(alice_client)

        _, status, _ = alice_api.service_login_with_http_info('authn-ldap', 'test', self.account)

        self.assertEqual(status, 200)

    def test_service_login_401(self):
        """Test case for service_login 401 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.bad_auth_api.service_login('iam', 'aws', self.account)

        self.assertEqual(context.exception.status, 401)

    def test_authenticate_service_200(self):
        """Test case for service_login 200 response

        Login with the given authenticator
        """
        alice_config = api_config.get_api_config(username='alice')
        alice_client = openapi_client.ApiClient(alice_config)
        alice_api = openapi_client.api.authn_api.AuthnApi(alice_client)

        _, status, _ = alice_api.authenticate_service_with_http_info(
            'authn-ldap',
            'test',
            self.account,
            'alice',
            'alice'
        )

        self.assertEqual(status, 200)

    def test_authenticate_service_401(self):
        """Test case for authenticate_service 401 response

        Login with the given authenticator
        """
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.authenticate_service(
                'authn-ldap',
                'test',
                self.account,
                'admin',
                'test'
            )

        self.assertEqual(context.exception.status, 401)

    def test_authenticate_service_404(self):
        """Test case for authenticate_service 404 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.authenticate_service('nonexist', 'nonexist', self.account, 'admin', 'badpass')

        self.assertEqual(context.exception.status, 404)


if __name__ == '__main__':
    unittest.main()
