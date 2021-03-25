from __future__ import absolute_import

import unittest
import base64

import openapi_client
import openapi_client.apis

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
        self.api = openapi_client.apis.SecretsApi(self.client)
        self.bad_auth_api = openapi_client.apis.SecretsApi(self.bad_auth_client)

    def grant_insufficient_permissions(self):
        """Loads a policy with incorrect permissions on a secret so we can retrieve
        a 403 error when we try to manipulate it"""
        policy_api = openapi_client.apis.PoliciesApi(self.client)

        policy_api.modify_policy(self.account, 'root', GRANT_POLICY)

    def test_create_variable_201(self):
        """Test case for create_variable response 201

        Creates a secret value within the specified variable.
        """
        secret_val = "this is a secret"

        resp = self.api.create_variable(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            body=secret_val,
            _return_http_data_only=False,
        )
        self.assertEqual(resp[1], 201)

    def test_create_variable_401(self):
        """Test case for create_variable response 401"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.bad_auth_api.create_variable(
                self.account,
                "variable",
                TEST_VARIABLES[0],
                body='test'
            )

        self.assertEqual(context.exception.status, 401)

    def test_create_variable_403(self):
        """Test case for create_variable response 403"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = openapi_client.apis.SecretsApi(alice_client)
        secret_val = "this is a secret"
        self.grant_insufficient_permissions()

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            alice_api.create_variable(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        self.assertEqual(context.exception.status, 403)

    def test_create_variable_422(self):
        """Test case for create_variable response 422"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.create_variable(self.account, "variable", TEST_VARIABLES[0], body="")

        self.assertEqual(context.exception.status, 422)

    def test_create_variable_expirations_201(self):
        """Test case for create_variable with expirations query parameter 201 response code"""
        _, status, _ = self.api.create_variable(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            expirations="",
            _return_http_data_only=False
        )

        self.assertEqual(status, 201)

    def test_create_variable_expirations_401(self):
        """Test case for create_variable with expirations query parameter 401 response code"""
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.create_variable(
                self.account,
                "variable",
                TEST_VARIABLES[0],
                expirations="",
            )

        self.assertEqual(context.exception.status, 401)

    def test_create_variable_expirations_403(self):
        """Test case for create_variable with expirations query parameter 403 response code"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = openapi_client.apis.SecretsApi(alice_client)
        self.grant_insufficient_permissions()

        with self.assertRaises(openapi_client.ApiException) as context:
            alice_api.create_variable(
                self.account,
                "variable",
                TEST_VARIABLES[0],
                expirations="",
            )

        self.assertEqual(context.exception.status, 403)

    def test_create_variable_expirations_404(self):
        """Test case for create_variable with expirations query parameter 404 response code"""
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.create_variable(
                self.account,
                "variable",
                'nonexist',
                expirations="",
            )

        self.assertEqual(context.exception.status, 404)

    def test_get_variable_version_200(self):
        """Test case for get_variable 200 response with version parameter

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create_variable(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        response = self.api.get_variable(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            version='2',
            _return_http_data_only=False
        )
        self.assertEqual(secret_val, response[0])
        self.assertEqual(response[1], 200)

    def test_get_variable_200(self):
        """Test case for get_variable 200 response

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create_variable(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        response = self.api.get_variable(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            _return_http_data_only=False
        )
        self.assertEqual(secret_val, response[0])
        self.assertEqual(response[1], 200)

    def test_get_variable_401(self):
        """Test case for get_variable 401 response with version parameter

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create_variable(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.bad_auth_api.get_variable(self.account, "variable", TEST_VARIABLES[0], version=1)

        self.assertEqual(context.exception.status, 401)

    def test_get_variable_version_401(self):
        """Test case for get_variable 401 response"""
        secret_val = "secret data"
        self.api.create_variable(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.bad_auth_api.get_variable(self.account, "variable", TEST_VARIABLES[0])

        self.assertEqual(context.exception.status, 401)

    def test_get_variable_403(self):
        """Test case for get_variable 403 response"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = openapi_client.apis.SecretsApi(alice_client)
        self.grant_insufficient_permissions()

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            alice_api.get_variable(self.account, "variable", TEST_VARIABLES[0])

        self.assertEqual(context.exception.status, 403)

    def test_get_variable_404(self):
        """Test case for get_variable 404 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.get_variable(self.account, "variable", "badname")

        self.assertEqual(context.exception.status, 404)

    def test_get_variable_422(self):
        """Test case for get_variable 422 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.get_variable(self.account, "variable", TEST_VARIABLES[0], version='')

        self.assertEqual(context.exception.status, 422)

    def set_variables(self, variables, values):
        """Sets the values of an array of variables"""
        for secret, value in zip(variables, values):
            self.api.create_variable(self.account, "variable", secret, body=value)

    def test_get_variables_200(self):
        """Test case for get_variables 200 response

        Fetch multiple secrets
        """
        secret_values = ['one', 'two']
        self.set_variables(TEST_VARIABLES, secret_values)

        # Secrets have to be in the format org:variable:secret_name
        secret_list = [f"dev:variable:{i}" for i in TEST_VARIABLES]
        response, status, _ = self.api.get_variables(
            ",".join(secret_list),
            _return_http_data_only=False
        )

        self.assertEqual(status, 200)
        for secret, value in zip(secret_list, secret_values):
            self.assertIn(secret, response)
            self.assertEqual(response[secret], value)

    def test_get_variables_401(self):
        """Test case for get_variables 401 response"""
        secret_list = ','.join([f"dev:variable:{i}" for i in TEST_VARIABLES])

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.bad_auth_api.get_variables(secret_list)

        self.assertEqual(context.exception.status, 401)

    def test_get_variables_403(self):
        """Test case for get_variables 403 response"""
        self.grant_insufficient_permissions()
        alice_client = api_config.get_api_client(username='alice')
        alice_api = openapi_client.apis.SecretsApi(alice_client)
        secret_list = ','.join([f"dev:variable:{i}" for i in TEST_VARIABLES])

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            alice_api.get_variables(secret_list)

        self.assertEqual(context.exception.status, 403)

    def test_get_variables_404(self):
        """Test case for get_variables 404 response"""
        secret_list = f'{self.account}:variable:nonexist'

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.get_variables(secret_list)

        self.assertEqual(context.exception.status, 404)

    def test_get_variables_422(self):
        """Test case for get_variables 422 response"""
        secret_list = "\00"

        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.api.get_variables(secret_list)

        self.assertEqual(context.exception.status, 422)

    def test_get_variables_encoded(self):
        """Test case for get_variables 200 response with base64 encoded binary secrets"""
        secret_values = [b'one\xffbinary', b'two']
        self.set_variables(TEST_VARIABLES, secret_values)

        # Secrets have to be in the format org:variable:secret_name
        secret_list = [f"dev:variable:{i}" for i in TEST_VARIABLES]
        response, status, headers = self.api.get_variables(
            ",".join(secret_list),
            accept_encoding="base64",
            _return_http_data_only=False
        )

        for secret, value in zip(secret_list, secret_values):
            self.assertIn(secret, response)
            decoded = base64.b64decode(response[secret])
            self.assertEqual(decoded, value)

        self.assertEqual(status, 200)
        self.assertEqual(headers['Content-Encoding'].lower(), "base64")

if __name__ == '__main__':
    unittest.main()
