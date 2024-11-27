from __future__ import absolute_import

import unittest
from unittest.mock import patch

import conjur

from . import api_config

TEST_VARIABLES = ["one/password", "testSecret"]

GRANT_POLICY = f"""
- !permit
  role: !user alice
  privileges: [ read ]
  resource: !variable {TEST_VARIABLES[0]}
"""

class TestSecretsApi(api_config.ConfiguredTest):
    """SecretsApi unit test stubs"""
    def setUp(self):
        self.api = conjur.api.secrets_api.SecretsApi(self.client)
        self.bad_auth_api = conjur.api.secrets_api.SecretsApi(self.bad_auth_client)

    def grant_insufficient_permissions(self):
        """Loads a policy with incorrect permissions on a secret so we can retrieve
        a 403 error when we try to manipulate it"""
        policy_api = conjur.api.PoliciesApi(self.client)

        policy_api.update_policy(self.account, 'root', GRANT_POLICY)

    def test_create_secret_201(self):
        """Test case for create_secret response 201

        Creates a secret value within the specified variable.
        """
        secret_val = "this is a secret"

        resp = self.api.create_secret_with_http_info(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            body=secret_val
        )
        self.assertEqual(resp[1], 201)

    def test_create_secret_401(self):
        """Test case for create_secret response 401"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.create_secret(
                self.account,
                "variable",
                TEST_VARIABLES[0],
                body='test'
            )

        self.assertEqual(context.exception.status, 401)

    def test_create_secret_403(self):
        """Test case for create_secret response 403"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.SecretsApi(alice_client)
        secret_val = "this is a secret"
        self.grant_insufficient_permissions()

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            alice_api.create_secret(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        self.assertEqual(context.exception.status, 403)

    def test_create_secret_422(self):
        """Test case for create_secret response 422"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.create_secret(self.account, "variable", TEST_VARIABLES[0], body="")

        self.assertEqual(context.exception.status, 422)

    def test_create_secret_expirations_201(self):
        """Test case for create_secret with expirations query parameter 201 response code"""
        _, status, _ = self.api.create_secret_with_http_info(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            expirations="",
        )

        self.assertEqual(status, 201)

    def test_create_secret_expirations_401(self):
        """Test case for create_secret with expirations query parameter 401 response code"""
        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.create_secret(
                self.account,
                "variable",
                TEST_VARIABLES[0],
                expirations="",
            )

        self.assertEqual(context.exception.status, 401)

    def test_create_secret_expirations_403(self):
        """Test case for create_secret with expirations query parameter 403 response code"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.SecretsApi(alice_client)
        self.grant_insufficient_permissions()

        with self.assertRaises(conjur.ApiException) as context:
            alice_api.create_secret(
                self.account,
                "variable",
                TEST_VARIABLES[0],
                expirations="",
            )

        self.assertEqual(context.exception.status, 403)

    def test_create_secret_expirations_404(self):
        """Test case for create_secret with expirations query parameter 404 response code"""
        with self.assertRaises(conjur.ApiException) as context:
            self.api.create_secret(
                self.account,
                "variable",
                'nonexist',
                expirations="",
            )

        self.assertEqual(context.exception.status, 404)

    def test_get_secret_version_200(self):
        """Test case for get_secret 200 response with version parameter

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create_secret(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        response = self.api.get_secret_with_http_info(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            version=2
        )
        self.assertEqual(secret_val, response[0])
        self.assertEqual(response[1], 200)

    def test_get_secret_200(self):
        """Test case for get_secret 200 response

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create_secret(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        response = self.api.get_secret_with_http_info(self.account, "variable", TEST_VARIABLES[0])
        self.assertEqual(secret_val, response[0])
        self.assertEqual(response[1], 200)

    def test_get_secret_401(self):
        """Test case for get_secret 401 response with version parameter

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create_secret(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.get_secret(self.account, "variable", TEST_VARIABLES[0], version=1)

        self.assertEqual(context.exception.status, 401)

    def test_get_secret_version_401(self):
        """Test case for get_secret 401 response"""
        secret_val = "secret data"
        self.api.create_secret(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.get_secret(self.account, "variable", TEST_VARIABLES[0])

        self.assertEqual(context.exception.status, 401)

    def test_get_secret_403(self):
        """Test case for get_secret 403 response"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.SecretsApi(alice_client)
        self.grant_insufficient_permissions()

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            alice_api.get_secret(self.account, "variable", TEST_VARIABLES[0])

        self.assertEqual(context.exception.status, 403)

    def test_get_secret_404(self):
        """Test case for get_secret 404 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_secret(self.account, "variable", "badname")

        self.assertEqual(context.exception.status, 404)

    def set_variables(self, variables, values):
        """Sets the values of an array of variables"""
        for secret, value in zip(variables, values):
            self.api.create_secret(self.account, "variable", secret, body=value)

    def test_get_secrets_200(self):
        """Test case for get_secrets 200 response

        Fetch multiple secrets
        """
        secret_values = ['one', 'two']
        self.set_variables(TEST_VARIABLES, secret_values)

        # Secrets have to be in the format org:variable:secret_name
        secret_list = [f"{self.account}:variable:{i}" for i in TEST_VARIABLES]
        response, status, _ = self.api.get_secrets_with_http_info(
            ",".join(secret_list)
        )

        self.assertEqual(status, 200)
        for secret, value in zip(secret_list, secret_values):
            self.assertIn(secret, response)
            self.assertEqual(response[secret], value)

    def test_get_secrets_401(self):
        """Test case for get_secrets 401 response"""
        secret_list = ','.join([f"{self.account}:variable:{i}" for i in TEST_VARIABLES])

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.get_secrets(secret_list)

        self.assertEqual(context.exception.status, 401)

    def test_get_secrets_403(self):
        """Test case for get_secrets 403 response"""
        self.grant_insufficient_permissions()
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.SecretsApi(alice_client)
        secret_list = ','.join([f"{self.account}:variable:{i}" for i in TEST_VARIABLES])

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            alice_api.get_secrets(secret_list)

        self.assertEqual(context.exception.status, 403)

    def test_get_secrets_404(self):
        """Test case for get_secrets 404 response"""
        secret_list = f'{self.account}:variable:nonexist'

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_secrets(secret_list)

        self.assertEqual(context.exception.status, 404)

    def test_get_secrets_422(self):
        """Test case for get_secrets 422 response"""
        secret_list = "\00"

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.get_secrets(secret_list)

        self.assertEqual(context.exception.status, 422)

    def test_get_secrets_encoded(self):
        """Test case for get_secrets 200 response with base64 encoded binary secrets"""
        secret_values = [b'one\xffbinary', b'two']
        self.set_variables(TEST_VARIABLES, secret_values)

        # Secrets have to be in the format org:variable:secret_name
        secret_list = [f"{self.account}:variable:{i}" for i in TEST_VARIABLES]
        with patch.object(conjur.api_client.ApiClient, 'call_api', return_value=None) \
                as mock:
            self.api.get_secrets(
                ",".join(secret_list),
                accept_encoding="base64"
            )
        mock.assert_called_once_with(
            '/secrets',
            'GET',
            {},
            [('variable_ids', ','.join(secret_list))],
            {'Accept-Encoding': 'base64', 'Accept': 'application/json'},
            body=None,
            post_params=[],
            files={},
            response_type='object',
            auth_settings=['conjurAuth'],
            async_req=None,
            _return_http_data_only=True,
            _preload_content=True,
            _request_timeout=None,
            collection_formats={}
        )

if __name__ == '__main__':
    unittest.main()
