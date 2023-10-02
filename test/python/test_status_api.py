from __future__ import absolute_import

import unittest
from unittest.mock import patch

from conjur import ApiClient, ApiException
from conjur.api import PoliciesApi, SecretsApi, StatusApi
from conjur.models import AuthenticatorsResponse, WhoAmI

from . import api_config

AUTHENTICATOR_FIELDS = [
    "enabled",
    "installed",
    "configured",
]

WHOAMI_FIELDS = [
    "client_ip",
    "user_agent",
    "account",
    "username",
    "token_issued_at",
]

class TestStatusApi(api_config.ConfiguredTest):
    """StatusApi unit test stubs"""
    @classmethod
    def setup_webservice(cls):
        """loads the webservice policy into conjur and gets it setup"""
        policies_api = PoliciesApi(cls.client)
        secrets_api = SecretsApi(cls.client)
        policies_api.update_policy(cls.account, 'root', api_config.get_webservice_policy())
        secrets_api.create_secret(
            cls.account,
            "variable",
            'conjur/authn-oidc/okta/provider-uri',
            body='invalid'
        )
        secrets_api.create_secret(
            cls.account,
            "variable",
            'conjur/authn-oidc/okta/id-token-user-property',
            body='admin'
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_webservice()

    def setUp(self):
        self.api = StatusApi(self.client)
        self.bad_auth_api = StatusApi(self.bad_auth_client)

    def test_who_am_i_200(self):
        """Test case for who_am_i 200 response"""
        result = self.api.who_am_i()

        self.assertIsInstance(result, WhoAmI)

        for i in WHOAMI_FIELDS:
            value = getattr(result, i)
            # Just make sure that all the attributes have a value assigned to them
            self.assertNotEqual(value, '')

    def test_who_am_i_401(self):
        """Test case for who_am_i 401 response"""
        with self.assertRaises(ApiException) as context:
            self.bad_auth_api.who_am_i()

        self.assertEqual(context.exception.status, 401)

    @unittest.skipIf(api_config.ENTERPRISE_TESTS,
                     'Dont support testing external authenticators on Enterprise currently')
    def test_get_service_authenticator_status_200(self):
        """Test case for get_service_authenticator_status 200 return code"""
        api_config.setup_oidc_webservice()
        response = self.api.get_service_authenticator_status_with_http_info(
            'authn-oidc',
            'test',
            self.account
        )
        self.assertEqual(response.data.status, 'ok')
        self.assertEqual(response.status_code, 200)

        with patch.object(ApiClient, 'call_api', return_value=None) \
                as mock:
            self.api.get_service_authenticator_status('authn-azure', 'test', self.account)

        mock.assert_called_once_with(
            '/{authenticator}/{service_id}/{account}/status',
            'GET',
            {
                'account': self.account,
                'authenticator': 'authn-azure',
                'service_id': 'test'
            },
            [],
            {'Accept': 'application/json'},
            body=None,
            files={},
            post_params=[],
            response_types_map={
                '200': 'AuthenticatorStatus',
                '400': None,
                '401': None,
                '403': None,
                '404': None,
                '500': 'AuthenticatorStatus',
                '501': 'AuthenticatorStatus'
            },
            auth_settings=['conjurAuth'],
            async_req=None,
            _return_http_data_only=True,
            _preload_content=True,
            _request_timeout=None,
            collection_formats={},
            _request_auth=None
        )

    def test_get_service_authenticator_status_403(self):
        """Test case for get_service_authenticator_status 403 return code"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = StatusApi(alice_client)

        with self.assertRaises(ApiException) as context:
            alice_api.get_service_authenticator_status('authn-oidc', 'okta', self.account)

        self.assertEqual(context.exception.status, 403)

    def test_get_service_authenticator_status_404(self):
        """Test case for get_service_authenticator_status 404 return code"""
        with self.assertRaises(ApiException) as context:
            self.api.get_service_authenticator_status('nonexist', 'test', self.account)

        self.assertEqual(context.exception.status, 404)

    def test_get_service_authenticator_status_500(self):
        """Test case for get_service_authenticator_status 500 return code"""
        with self.assertRaises(ApiException) as context:
            self.api.get_service_authenticator_status('authn-oidc', 'okta', self.account)

        self.assertEqual(context.exception.status, 500)

    def test_get_service_authenticator_status_501(self):
        """Test case for get_service_authenticator_status 500 return code"""
        with self.assertRaises(ApiException) as context:
            self.api.get_service_authenticator_status('authn-ldap', 'test', self.account)

        self.assertEqual(context.exception.status, 501)

    def test_get_gcp_authenticator_status_200(self):
        """Test case for get_gcp_authenticator_status 200 return code"""
        with patch.object(ApiClient, 'call_api', return_value=None) as mock:
            self.api.get_gcp_authenticator_status(self.account)

        mock.assert_called_once_with(
            '/authn-gcp/{account}/status',
            'GET',
            { 'account': self.account },
            [],
            { 'Accept': 'application/json' },
            body=None,
            files={},
            post_params=[],
            response_types_map={
                '200': 'AuthenticatorStatus',
                '400': None,
                '403': None,
                '404': None,
                '500': 'AuthenticatorStatus',
                '501': 'AuthenticatorStatus'
            },
            auth_settings=['conjurAuth'],
            async_req=None,
            _return_http_data_only=True,
            _preload_content=True,
            _request_timeout=None,
            collection_formats={},
            _request_auth=None
        )

    def test_get_gcp_authenticator_status_403(self):
        """Test case for get_gcp_authenticator_status 403 return code"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = StatusApi(alice_client)

        with self.assertRaises(ApiException) as context:
            alice_api.get_gcp_authenticator_status(self.account)

        self.assertEqual(context.exception.status, 403)

    def test_get_gcp_authenticator_status_500(self):
        """Test case for get_gcp_authenticator_status 500 return code"""
        with self.assertRaises(ApiException) as context:
            self.api.get_gcp_authenticator_status(self.account)

        self.assertEqual(context.exception.status, 500)

    def test_get_authenticators_200(self):
        """Test case for authenticators 200 response"""
        response = self.api.get_authenticators_with_http_info()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(
            response.data,
            AuthenticatorsResponse
        )

        for i in AUTHENTICATOR_FIELDS:
            lst  = getattr(response.data, i)
            self.assertIsInstance(lst, list)
            # authn is the default authenticator so it will always be installed and enabled
            self.assertIn('authn', lst)

            for value in lst:
                self.assertIsInstance(value, str)
                self.assertNotEqual(value, '')

    def test_set_request_id(self):
        """Test case for setting the request ID on an endpoint"""
        request_id = 'testing'
        response = self.api.get_authenticators_with_http_info(
            x_request_id=request_id,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Request-Id'], request_id)

    @unittest.skipUnless(api_config.ENTERPRISE_TESTS, "Endpoint not available in Conjur")
    def test_health_200(self):
        """Test case for Enterprise health 200 response"""
        response = self.api.health_with_http_info()
        status_keys = ['services', 'audit', 'database']

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['ok'])
        for i in status_keys:
            self.assertTrue(response.data[i]['ok'])

    @unittest.skipUnless(api_config.ENTERPRISE_TESTS, "Endpoint not available in Conjur")
    def test_remote_health_200(self):
        """Test case for Enterprise remote health 200 response"""
        response = self.api.remote_health_with_http_info(
            'conjur-master.mycompany.local'
        )
        status_keys = ['services', 'audit', 'database']

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['ok'])
        for i in status_keys:
            self.assertTrue(response.data[i]['ok'])

    @unittest.skipUnless(api_config.ENTERPRISE_TESTS, "Endpoint not available in Conjur")
    def test_info_200(self):
        """Test case for Enterprise info 200 response"""
        response = self.api.info_with_http_info()
        keys = [
            'release',
            'version',
            'services',
            'container',
            'role',
            'configuration',
            'authenticators'
        ]

        self.assertEqual(response.status_code, 200)
        for i in keys:
            self.assertIsNotNone(getattr(response.data, i))

if __name__ == '__main__':
    unittest.main()
