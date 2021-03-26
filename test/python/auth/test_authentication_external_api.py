from __future__ import absolute_import

import unittest
from unittest.mock import patch
import json

import requests
import conjur

from .. import api_config

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

@unittest.skipIf(api_config.ENTERPRISE_TESTS, 'No environment available for Enterprise')
class TestExternalAuthnApi(api_config.ConfiguredTest):
    """Class tests api functions relating to external authenticators

    Separate from the Authn tests to avoid issues with changing api keys/paswords
    """
    def setUp(self):
        self.api = conjur.api.AuthenticationApi(self.client)
        self.bad_auth_api = conjur.api.AuthenticationApi(self.bad_auth_client)

    def test_enable_authenticator_instance_204(self):
        """Test case for enable_authenticator_instance 204 response

        Updates the authenticators configuration
        """
        _, status, _ = self.api.enable_authenticator_instance_with_http_info(
            'authn-ldap',
            'test',
            self.account,
            enabled=True
        )

        self.assertEqual(status, 204)

    def test_enable_authenticator_instance_401(self):
        """Test case for enable_authenticator_instance 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.enable_authenticator_instance(
                'oidc',
                'okta',
                self.account,
                enabled=False
            )

        self.assertEqual(context.exception.status, 401)

    def test_enable_authenticator_instance_404(self):
        """Test case for enable_authenticator_instance 404 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.enable_authenticator_instance(
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
        alice_client = conjur.ApiClient(alice_config)
        alice_api = conjur.api.AuthenticationApi(alice_client)

        _, status, _ = alice_api.get_api_key_via_ldap_with_http_info('test', self.account)

        self.assertEqual(status, 200)

    def test_service_login_401(self):
        """Test case for service_login 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.get_api_key_via_ldap('aws', self.account)

        self.assertEqual(context.exception.status, 401)

    def test_get_access_token_service_200(self):
        """Test case for get_access_token_service 200 response

        Login with the given authenticator
        """
        alice_config = api_config.get_api_config(username='alice')
        alice_client = conjur.ApiClient(alice_config)
        alice_api = conjur.api.AuthenticationApi(alice_client)

        _, status, _ = alice_api.get_access_token_via_ldap_with_http_info(
            'test',
            self.account,
            'alice',
            body='alice'
        )

        self.assertEqual(status, 200)

    def test_get_access_token_service_401(self):
        """Test case for get_access_token_service 401 response

        Login with the given authenticator
        """
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_access_token_via_ldap(
                'test',
                self.account,
                'admin',
                body='test'
            )

        self.assertEqual(context.exception.status, 401)

# we should write one of these for each service; commenting out for now
#    def test_get_access_token_service_404(self):
#        """Test case for authenticate_service 404 response"""
#        with self.assertRaises(conjur.exceptions.ApiException) as context:
#            self.api.get_access_token_via_authenticator(
#                'nonexist',
#                'nonexist',
#                self.account,
#                'admin',
#                body='badpass'
#            )
#
#        self.assertEqual(context.exception.status, 404)

    def test_oidc_authenticate_200(self):
        """Test case for oidc_authenticate 200 response"""
        api_config.setup_oidc_webservice()
        id_token = get_oidc_id_token()

        _, status, _ = self.api.get_access_token_via_oidc_with_http_info(
            'test',
            self.account,
            id_token=id_token
        )
        self.assertEqual(status, 200)

    def test_oidc_authenticate_401(self):
        """Test case for oidc_authenticate 401 response"""
        api_config.setup_oidc_webservice()

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_access_token_via_oidc('test', self.account, id_token='bad-token')

        self.assertEqual(context.exception.status, 401)

    def test_gcp_authenticate_200(self):
        """Test case for gcp_authenticate 200 response"""
        jwt_token = 'bad token'

        with patch.object(conjur.ApiClient, 'call_api', return_value=None) \
                as mock:
            self.api.get_access_token_via_gcp(self.account, jwt=jwt_token)

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
            auth_settings=['basicAuth','conjurAuth','conjurKubernetesMutualTls'],
            async_req=None,
            _return_http_data_only=True,
            _preload_content=True,
            _request_timeout=None,
            collection_formats={}
        )

    def test_gcp_authenticate_400(self):
        """Test case for gcp_authenticate 400 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_access_token_via_gcp('\00', jwt='bad token')

        self.assertEqual(context.exception.status, 400)

    def test_gcp_authenticate_401(self):
        """Test case for gcp_authenticate 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_access_token_via_gcp(self.account, jwt='bad token')

        self.assertEqual(context.exception.status, 401)

if __name__ == '__main__':
    unittest.main()
