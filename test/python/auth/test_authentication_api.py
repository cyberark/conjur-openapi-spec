from __future__ import absolute_import

import json
import os
import unittest

import conjur

from .. import api_config
from ..api_config import CONJUR_AUTHN_API_KEY


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

        self.client = conjur.ApiClient(self.config)
        self.api = conjur.api.AuthenticationApi(self.client)

        self.bad_auth_api = conjur.api.AuthenticationApi(self.bad_auth_client)

    def tearDown(self):
        self.client.close()

    def test_get_access_token_200(self):
        """Test case for get_access_token 200 response

        Gets a short-lived access token, which can be used to authenticate requests
        to (most of) the rest of the Conjur API.
        """
        response, status, _ = self.api.get_access_token_with_http_info(
            self.account,
            self.config.username,
            body=self.api_key
        )
        response_json = json.loads(response.replace("\'","\""))
        response_keys = response_json.keys()

        self.assertEqual(status, 200)
        self.assertIn("protected", response_keys)
        self.assertIn("payload", response_keys)
        self.assertIn("signature", response_keys)

    def test_get_access_token_400(self):
        """Test case for 400 status response when authenticating a user with Conjur
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.get_access_token(
                self.account,
                '\00',
                body=self.api_key
            )

        self.assertEqual(context.exception.status, 400)

    def test_get_access_token_401(self):
        """Test case for 401 status response when authenticating a user with Conjur
        401 - the request lacks valid authenticate credentials
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.get_access_token(
                self.account,
                self.config.username,
                body='bad_api_key'
            )

        self.assertEqual(context.exception.status, 401)

    def test_get_api_key_200(self):
        """Test case for 200 status response when logging in
        Gets the API key of a user given the username and password via HTTP Basic Authentication.
        """
        api_key, status, _ = self.api.get_api_key_with_http_info(self.account)

        self.assertEqual(status, 200)
        self.assertEqual(api_key, self.api_key)

    def test_get_api_key_400(self):
        """Test case for 400 status response when logging in
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.get_api_key('\00')

        self.assertEqual(context.exception.status, 400)

    def test_get_api_key_401(self):
        """Test case for 401 status response when loggin in
        401 - the request lacks valid authentication credentials
        """
        # Ensure we cannot login with a bad password
        self.config.password = "FakePassword123"

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_api_key(self.account)

        self.assertEqual(context.exception.status, 401)

    @unittest.skipIf(api_config.ENTERPRISE_TESTS,
         "Our Enterprise conf doesn't support bypassing ssl so we cannot evoke this response")
    def test_get_api_key_422(self):
        """Test case for 422 status response when logging in
        This test uses HTTP instead of HTTPS, letting Conjur reject malformed parameters
        that would otherwise be rejected by the NGINX proxy
        """
        self.config.host = 'http://conjur'

        with self.assertRaises(conjur.ApiException) as context:
            self.api.get_api_key('\00')

        self.assertEqual(context.exception.status, 422)

    def test_rotate_own_api_key_200a(self):
        """Test case A for 200 status response when rotating own API key
        Rotates a user’s own API key. The new key is in the response body.
        """
        # Rotate the key and attempt to login with it
        new_key, status, _ = self.api.rotate_api_key_with_http_info(
            self.account
        )
        self.assertEqual(status, 200)

        self.config.password = new_key
        self.api.get_api_key(self.account)

        # We rotated the API key so we have to update the class variable
        self.__class__.api_key = new_key

    def test_rotate_own_api_key_200b(self):
        """Test case B for 200 status response when rotating own API key
        Rotates a user's own API key by querying for itself. The new key is in the response body.
        """
        # Rotate the key and attempt to login with it
        new_key, status, _ = self.api.rotate_api_key_with_http_info(
            self.account,
            role=f'user:{self.config.username}'
        )
        self.assertEqual(status, 200)

        self.config.password = new_key
        self.api.get_api_key(self.account)

        # We rotated the API key so we have to update the class variable
        self.__class__.api_key = new_key

    def test_rotate_other_api_key_200(self):
        """Test case for 200 status response when rotating a foreign role's API key
        Rotates the specified role's own API key. The new key is in the response body.
        """
        authenticated_api = conjur.AuthenticationApi(api_config.get_api_client())

        new_key_alice, status, _ = authenticated_api.rotate_api_key_with_http_info(
            self.account,
            role='user:alice'
        )
        self.assertEqual(status, 200)

        # file deepcode ignore NoHardcodedCredentials/test: This is a test file
        self.config.username = 'alice'
        self.config.password = new_key_alice
        self.api.get_api_key(self.account)

        # reset api config
        self.config.username = 'admin'
        self.config.password = self.api_key

    def test_rotate_api_key_400(self):
        """Test case for 400 status response when rotating a user's API key
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.rotate_api_key('\00')

        self.assertEqual(context.exception.status, 400)

    def test_rotate_api_key_401(self):
        """Test case for 401 status response when rotating a user's API key
        401 - the request lacks valid authentication credentials
        """
        self.config.password = "FakePassword123"

        with self.assertRaises(conjur.ApiException) as context:
            self.api.rotate_api_key(self.account)

        self.assertEqual(context.exception.status, 401)

    def test_rotate_api_key_422(self):
        """Test case for 422 status response when logging in
        This test uses HTTP instead of HTTPS, letting Conjur reject malformed parameters
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.rotate_api_key(self.account, role='\00')

        self.assertEqual(context.exception.status, 422)

    def test_change_password_204(self):
        """Test case for changing password

        Changes a user’s password.
        """
        # Set a new password and try to authenticate with it
        test_password = "PAssword!234"

        _, status, _ = self.api.change_password_with_http_info(
            self.account,
            test_password
        )

        self.assertEqual(status, 204)

        self.config.password = test_password
        self.api.get_api_key(self.account)

    def test_change_password_400(self):
        """Test case for 400 status response when setting password
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.change_password('\00', 'PAssword!234')

        self.assertEqual(context.exception.status, 400)

    def test_change_password_401(self):
        """Test case for 401 status response when setting password
        401 - the request lacks valid authentication credentials
        """
        # Attempt to change password with bad auth info
        test_password = "PAssword!234"

        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.change_password(self.account, test_password)

        self.assertEqual(context.exception.status, 401)

        # Attempt to set the users password to something invalid
        invalid_pass = 'SomethingInvalid'

        with self.assertRaises(conjur.exceptions.ApiException):
            self.api.change_password(self.account, body=invalid_pass)

    def test_change_password_422(self):
        """Test case for 422 status response when setting password
        422 - Conjur received a malformed parameter, password does not fit minimum requirements
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.change_password(self.account, 'bad-pass')

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
