from __future__ import absolute_import

import os
import unittest
from unittest.mock import patch
import json

import requests
import openapi_client

from . import api_config
from .api_config import CONJUR_AUTHN_API_KEY

def get_oidc_id_token():
    """Authenticates with the OIDC server and gets the ID token for user bob"""
    oidc_request_form = {
        'grant_type': 'password',
        'username': 'bob',
        'password': 'bob',
        'scope': 'openid'
    }
    result = requests.post(
        'http://oidc-keycloak:8080/auth/realms/master/protocol/openid-connect/token',
        data=oidc_request_form,
        auth=('conjurClient', '1234')
    )
    result = json.loads(result.content)
    return result['id_token']

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

    def test_authenticate_200(self):
        """Test case for authenticate

        Gets a short-lived access token, which can be used to authenticate requests
        to (most of) the rest of the Conjur API.
        """
        response, status, _ = self.api.authenticate_with_http_info(
            'authn',
            self.account,
            self.config.username,
            self.api_key
        )
        response_json = json.loads(response.replace("\'","\""))
        response_keys = response_json.keys()

        self.assertEqual(status, 200)
        self.assertIn("protected", response_keys)
        self.assertIn("payload", response_keys)
        self.assertIn("signature", response_keys)

    def test_authenticate_400(self):
        """Test case for 400 status response when authenticating a user with Conjur
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.authenticate(
                'authn',
                self.account,
                '\00',
                self.api_key
            )

        self.assertEqual(context.exception.status, 400)

    def test_authenticate_401(self):
        """Test case for 401 status response when authenticating a user with Conjur
        401 - the request lacks valid authenticate credentials
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.authenticate(
                'authn',
                self.account,
                self.config.username,
                'bad_api_key'
            )

        self.assertEqual(context.exception.status, 401)

    def test_login_200(self):
        """Test case for 200 status response when logging in
        Gets the API key of a user given the username and password via HTTP Basic Authentication.
        """
        api_key, status, _ = self.api.login_with_http_info('authn', self.account)

        self.assertEqual(status, 200)
        self.assertEqual(api_key, self.api_key)

    def test_login_400(self):
        """Test case for 400 status response when logging in
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.login('authn', '\00')

        self.assertEqual(context.exception.status, 400)

    def test_login_401(self):
        """Test case for 401 status response when loggin in
        401 - the request lacks valid authentication credentials
        """
        # Ensure we cannot login with a bad password
        self.config.password = "FakePassword123"

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.login('authn', self.account)

        self.assertEqual(context.exception.status, 401)

    def test_login_422(self):
        """Test case for 422 status response when logging in
        This test uses HTTP instead of HTTPS, letting Conjur reject malformed parameters
        that would otherwise be rejected by the NGINX proxy
        """
        self.config.host = 'http://conjur'

        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.login('authn', '\00')

        self.assertEqual(context.exception.status, 422)

    def test_rotate_own_api_key_200a(self):
        """Test case A for 200 status response when rotating own API key
        Rotates a user’s own API key. The new key is in the response body.
        """
        # Rotate the key and attempt to login with it
        new_key, status, _ = self.api.rotate_api_key_with_http_info(
            'authn',
            self.account
        )
        self.assertEqual(status, 200)

        self.config.password = new_key
        self.api.login('authn', self.account)

        # We rotated the API key so we have to update the class variable
        self.__class__.api_key = new_key

    def test_rotate_own_api_key_200b(self):
        """Test case B for 200 status response when rotating own API key
        Rotates a user's own API key by querying for itself. The new key is in the response body.
        """
        # Rotate the key and attempt to login with it
        new_key, status, _ = self.api.rotate_api_key_with_http_info(
            'authn',
            self.account,
            role=f'user:{self.config.username}'
        )
        self.assertEqual(status, 200)

        self.config.password = new_key
        self.api.login('authn', self.account)

        # We rotated the API key so we have to update the class variable
        self.__class__.api_key = new_key

    def test_rotate_other_api_key_200(self):
        """Test case for 200 status response when rotating a foreign role's API key
        Rotates the specified role's own API key. The new key is in the response body.
        """
        authenticated_api = openapi_client.AuthnApi(api_config.get_api_client())

        new_key_alice, status, _ = authenticated_api.rotate_api_key_with_http_info(
            'authn',
            self.account,
            role='user:alice'
        )
        self.assertEqual(status, 200)

        self.config.username = 'alice'
        self.config.password = new_key_alice
        self.api.login('authn', self.account)

        # reset api config
        self.config.username = 'admin'
        self.config.password = self.api_key

    def test_rotate_api_key_400(self):
        """Test case for 400 status response when rotating a user's API key
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.rotate_api_key('authn', '\00')

        self.assertEqual(context.exception.status, 400)

    def test_rotate_api_key_401(self):
        """Test case for 401 status response when rotating a user's API key
        401 - the request lacks valid authentication credentials
        """
        self.config.password = "FakePassword123"

        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.rotate_api_key('authn', self.account)

        self.assertEqual(context.exception.status, 401)

    def test_rotate_api_key_422(self):
        """Test case for 422 status response when logging in
        This test uses HTTP instead of HTTPS, letting Conjur reject malformed parameters
        """
        self.config.host = 'http://conjur'

        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.rotate_api_key('authn', self.account, role='\00')

        self.assertEqual(context.exception.status, 422)

    def test_set_password_204(self):
        """Test case for set_password

        Changes a user’s password.
        """
        # Set a new password and try to authenticate with it
        test_password = "PAssword!234"

        _, status, _ = self.api.set_password_with_http_info(
            self.account,
            test_password
        )

        self.assertEqual(status, 204)

        self.config.password = test_password
        self.api.login('authn', self.account)

    def test_set_password_400(self):
        """Test case for 400 status response when setting password
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.set_password('\00', 'PAssword!234')

        self.assertEqual(context.exception.status, 400)

    def test_set_password_401(self):
        """Test case for 401 status response when setting password
        401 - the request lacks valid authentication credentials
        """
        # Attempt to change password with bad auth info
        test_password = "PAssword!234"

        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.set_password(self.account, test_password)

        self.assertEqual(context.exception.status, 401)

        # Attempt to set the users password to something invalid
        invalid_pass = 'SomethingInvalid'

        with self.assertRaises(openapi_client.exceptions.ApiException):
            self.api.set_password(self.account, body=invalid_pass)

    def test_set_password_422(self):
        """Test case for 422 status response when setting password
        422 - Conjur received a malformed parameter, password does not fit minimum requirements
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.set_password(self.account, 'bad-pass')

        self.assertEqual(context.exception.status, 422)

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

    def test_oidc_authenticate_200(self):
        """Test case for oidc_authenticate 200 response"""
        api_config.setup_oidc_webservice()
        id_token = get_oidc_id_token()

        _, status, _ = self.api.oidc_authenticate_with_http_info(
            'test',
            self.account,
            id_token=id_token
        )
        self.assertEqual(status, 200)

    def test_oidc_authenticate_401(self):
        """Test case for oidc_authenticate 401 response"""
        api_config.setup_oidc_webservice()

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.oidc_authenticate('test', self.account, id_token='bad-token')

        self.assertEqual(context.exception.status, 401)

    def test_gcp_authenticate_200(self):
        """Test case for gcp_authenticate 200 response"""
        jwt_token = 'bad token'

        with patch.object(openapi_client.api_client.ApiClient, 'call_api', return_value=None) \
                as mock:
            self.api.gcp_authenticate(self.account, jwt=jwt_token)

        mock.assert_called_once_with(
            '/authn-gcp/{account}/authenticate',
            'POST',
            {'account': self.account},
            [],
            {'Accept': 'text/plain', 'Content-Type': 'application/x-www-form-urlencoded'},
            body=None,
            post_params=[('jwt', jwt_token)],
            files={},
            response_type='str',
            auth_settings=['basicAuth','conjurAuth'],
            async_req=None,
            _return_http_data_only=True,
            _preload_content=True,
            _request_timeout=None,
            collection_formats={}
        )

    def test_gcp_authenticate_400(self):
        """Test case for gcp_authenticate 400 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.gcp_authenticate('\00', jwt='bad token')

        self.assertEqual(context.exception.status, 400)

    def test_gcp_authenticate_401(self):
        """Test case for gcp_authenticate 401 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.gcp_authenticate(self.account, jwt='bad token')

        self.assertEqual(context.exception.status, 401)

if __name__ == '__main__':
    unittest.main()
