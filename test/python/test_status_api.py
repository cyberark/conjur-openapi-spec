from __future__ import absolute_import

import unittest
import pathlib

import openapi_client

from . import api_config

WHOAMI_FIELDS = [
    "client_ip",
    "user_agent",
    "account",
    "username",
    "token_issued_at",
]

WEBSERVICE_POLICY = pathlib.Path('test/config/webservice.yml')

def get_webservice_policy():
    """Gets the text for the webservice testing policy"""
    with open(WEBSERVICE_POLICY, 'r') as policy:
        return policy.read()

class TestStatusApi(api_config.ConfiguredTest):
    """StatusApi unit test stubs"""
    @classmethod
    def setup_webservice(cls):
        """loads the webservice policy into conjur and gets it setup"""
        policies_api = openapi_client.api.policies_api.PoliciesApi(cls.client)
        secrets_api = openapi_client.api.secrets_api.SecretsApi(cls.client)
        policies_api.modify_policy(cls.account, 'root', get_webservice_policy())
        secrets_api.create_variable(
            cls.account,
            "variable",
            'conjur/authn-oidc/okta/provider-uri',
            'invalid'
        )
        secrets_api.create_variable(
            cls.account,
            "variable",
            'conjur/authn-oidc/okta/id-token-user-property',
            'admin'
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_webservice()

    def setUp(self):
        self.api = openapi_client.api.status_api.StatusApi(self.client)
        self.bad_auth_api = openapi_client.api.status_api.StatusApi(self.bad_auth_client)

    def test_who_am_i_200(self):
        """Test case for who_am_i 200 response"""
        result = self.api.who_am_i()

        self.assertIsInstance(result, openapi_client.models.who_am_i.WhoAmI)

        for i in WHOAMI_FIELDS:
            value = getattr(result, i)
            # Just make sure that all the attributes have a value assigned to them
            self.assertNotEqual(value, '')

    def test_who_am_i_401(self):
        """Test case for who_am_i 401 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.bad_auth_api.who_am_i()

        self.assertEqual(context.exception.status, 401)

    @unittest.expectedFailure
    def test_authenticator_service_status_200(self):
        """Test case for authenticator_service_status 200 return code

        We currently do not test this, see https://github.com/cyberark/conjur-openapi-spec/issues/84
        """
        resp = self.api.authenticator_service_status('oidc', 'okta', self.account)
        self.assertEqual(resp['status'], 'ok')

    def test_authenticator_service_status_403(self):
        """Test case for authenticator_service_status 403 return code"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = openapi_client.api.status_api.StatusApi(alice_client)

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            alice_api.authenticator_service_status('oidc', 'okta', self.account)

        self.assertEqual(context.exception.status, 403)

    def test_authenticator_service_status_404(self):
        """Test case for authenticator_service_status 404 return code"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.authenticator_service_status('nonexist', 'test', self.account)

        self.assertEqual(context.exception.status, 404)

    def test_authenticator_service_status_500(self):
        """Test case for authenticator_service_status 500 return code"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.authenticator_service_status('oidc', 'okta', self.account)

        self.assertEqual(context.exception.status, 500)

    def test_authenticator_service_status_501(self):
        """Test case for authenticator_service_status 500 return code"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.authenticator_service_status('ldap', 'test', self.account)

        self.assertEqual(context.exception.status, 501)

    @unittest.expectedFailure
    def test_authenticator_status_200(self):
        """Test case for authenticator_status 200 return code

        We currently do not test this, see https://github.com/cyberark/conjur-openapi-spec/issues/84
        """
        resp = self.api.authenticator_status('azure', self.account)
        self.assertEqual(resp['status'], 'ok')

    def test_authenticator_status_403(self):
        """Test case for authenticator_status 403 return code"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = openapi_client.api.status_api.StatusApi(alice_client)

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            alice_api.authenticator_status('azure', self.account)

        self.assertEqual(context.exception.status, 403)

    def test_authenticator_status_404(self):
        """Test case for authenticator_status 404 return code"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.authenticator_status('nonexist', self.account)

        self.assertEqual(context.exception.status, 404)

    def test_authenticator_status_500(self):
        """Test case for authenticator_status 500 return code"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.authenticator_status('azure', self.account)

        self.assertEqual(context.exception.status, 500)

    def test_authenticator_status_501(self):
        """Test case for authenticator_status 501 return code"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.authenticator_status('ldap', self.account)

        self.assertEqual(context.exception.status, 501)

if __name__ == '__main__':
    unittest.main()
