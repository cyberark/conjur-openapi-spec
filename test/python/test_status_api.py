from __future__ import absolute_import

import unittest
from unittest.mock import patch

import conjur

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
        policies_api = conjur.api.policies_api.PoliciesApi(cls.client)
        secrets_api = conjur.api.secrets_api.SecretsApi(cls.client)
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
        self.api = conjur.api.status_api.StatusApi(self.client)
        self.bad_auth_api = conjur.api.status_api.StatusApi(self.bad_auth_client)

    def test_who_am_i_200(self):
        """Test case for who_am_i 200 response"""
        result = self.api.who_am_i()

        self.assertIsInstance(result, conjur.models.WhoAmI200Response)

        for i in WHOAMI_FIELDS:
            value = getattr(result, i)
            # Just make sure that all the attributes have a value assigned to them
            self.assertNotEqual(value, '')

    def test_who_am_i_401(self):
        """Test case for who_am_i 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.who_am_i()

        self.assertEqual(context.exception.status, 401)

    @unittest.skipIf(api_config.ENTERPRISE_TESTS,
                     'Dont support testing external authenticators on Enterprise currently')
    def test_get_service_authenticator_status_200(self):
        """Test case for get_service_authenticator_status 200 return code"""
        api_config.setup_oidc_webservice()
        res = self.api.get_service_authenticator_status_with_http_info(
            'authn-oidc',
            'test',
            self.account
        )
        self.assertEqual(res.status_code, 200)

        authn = 'authn-azure'
        service_id = 'test'
        res_body = b'{"error": null, "status": "enabled"}'
        mocked_response = api_config.get_mocked_rest_response(data=res_body)

        with patch.object(conjur.api_client.ApiClient, 'call_api', return_value=mocked_response) as mock:
            self.api.get_service_authenticator_status(authn, service_id, self.account)

        mock.assert_called_once_with(
            'GET',
            f'{self.client.configuration.host}/{authn}/{service_id}/{self.account}/status',
            {
                'Accept': 'application/json',
                'User-Agent': self.client.user_agent,
                'Authorization': f'Token {self.client.configuration.api_key["conjurAuth"]}',
            },
            None,
            [],
            _request_timeout=None,
        )

    def test_get_service_authenticator_status_403(self):
        """Test case for get_service_authenticator_status 403 return code"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.status_api.StatusApi(alice_client)

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            alice_api.get_service_authenticator_status('authn-oidc', 'okta', self.account)

        self.assertEqual(context.exception.status, 403)

    def test_get_service_authenticator_status_404(self):
        """Test case for get_service_authenticator_status 404 return code"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_service_authenticator_status('nonexist', 'test', self.account)

        self.assertEqual(context.exception.status, 404)

    def test_get_service_authenticator_status_500(self):
        """Test case for get_service_authenticator_status 500 return code"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_service_authenticator_status('authn-oidc', 'okta', self.account)

        self.assertEqual(context.exception.status, 500)

    def test_get_service_authenticator_status_501(self):
        """Test case for get_service_authenticator_status 500 return code"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_service_authenticator_status('authn-ldap', 'test', self.account)

        self.assertEqual(context.exception.status, 501)

    def test_get_gcp_authenticator_status_200(self):
        """Test case for get_gcp_authenticator_status 200 return code"""
        res_body = b'{"error": null, "status": "enabled"}'
        mocked_response = api_config.get_mocked_rest_response(data=res_body)
        with patch.object(conjur.api_client.ApiClient, 'call_api', return_value=mocked_response) as mock:
            self.api.get_gcp_authenticator_status(self.account)

        mock.assert_called_once_with(
            'GET',
            f'{self.client.configuration.host}/authn-gcp/{self.account}/status',
            {
                'Accept': 'application/json',
                'User-Agent': self.client.user_agent,
                'Authorization': f'Token {self.client.configuration.api_key["conjurAuth"]}',
            },
            None,
            [],
            _request_timeout=None,
        )

    def test_get_gcp_authenticator_status_403(self):
        """Test case for get_gcp_authenticator_status 403 return code"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.status_api.StatusApi(alice_client)

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            alice_api.get_gcp_authenticator_status(self.account)

        self.assertEqual(context.exception.status, 403)

    def test_get_gcp_authenticator_status_500(self):
        """Test case for get_gcp_authenticator_status 500 return code"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_gcp_authenticator_status(self.account)

        self.assertEqual(context.exception.status, 500)

    def test_get_authenticators_200(self):
        """Test case for authenticators 200 response"""
        res = self.api.get_authenticators_with_http_info()

        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(
            res.data,
            conjur.models.GetAuthenticators200Response
        )

        for i in AUTHENTICATOR_FIELDS:
            lst = getattr(res.data, i)
            self.assertIsInstance(lst, list)
            # authn is the default authenticator so it will always be installed and enabled
            self.assertIn('authn', lst)

            for value in lst:
                self.assertIsInstance(value, str)
                self.assertNotEqual(value, '')

    def test_set_request_id(self):
        """Test case for setting the request ID on an endpoint"""
        request_id = 'testing'
        res = self.api.get_authenticators_with_http_info(x_request_id=request_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['X-Request-Id'], request_id)

    @unittest.skipUnless(api_config.ENTERPRISE_TESTS, "Endpoint not available in Conjur")
    def test_health_200(self):
        """Test case for Enterprise health 200 response"""
        res= self.api.health_with_http_info()
        status_keys = ['services', 'audit', 'database']

        self.assertEqual(res.status_code, 200)
        for i in status_keys:
            self.assertTrue(res.data[i]['ok'])

    @unittest.skipUnless(api_config.ENTERPRISE_TESTS, "Endpoint not available in Conjur")
    def test_remote_health_200(self):
        """Test case for Enterprise remote health 200 response"""
        res = self.api.remote_health_with_http_info('conjur-master.mycompany.local')
        status_keys = ['services', 'audit', 'database']

        self.assertEqual(res.status_code, 200)
        for i in status_keys:
            self.assertTrue(res.data[i]['ok'])

    @unittest.skipUnless(api_config.ENTERPRISE_TESTS, "Endpoint not available in Conjur")
    def test_info_200(self):
        """Test case for Enterprise info 200 response"""
        res = self.api.info_with_http_info()
        keys = [
            'release',
            'version',
            'services',
            'container',
            'role',
            'configuration',
            'authenticators'
        ]

        self.assertEqual(res.status_code, 200)
        for i in keys:
            self.assertIsNotNone(getattr(res.data, i))


if __name__ == '__main__':
    unittest.main()
