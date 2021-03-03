from __future__ import absolute_import

import unittest

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

        policy_api.update(self.account, 'root', GRANT_POLICY)

    def test_create_201(self):
        """Test case for create response 201

        Creates a secret value within the specified variable.
        """
        secret_val = "this is a secret"

        resp = self.api.create_with_http_info(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            body=secret_val
        )
        self.assertEqual(resp[1], 201)

    def test_create_401(self):
        """Test case for create response 401"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.create(
                self.account,
                "variable",
                TEST_VARIABLES[0],
                body='test'
            )

        self.assertEqual(context.exception.status, 401)

    def test_create_403(self):
        """Test case for create response 403"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.SecretsApi(alice_client)
        secret_val = "this is a secret"
        self.grant_insufficient_permissions()

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            alice_api.create(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        self.assertEqual(context.exception.status, 403)

    def test_create_422(self):
        """Test case for create response 422"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.create(self.account, "variable", TEST_VARIABLES[0], body="")

        self.assertEqual(context.exception.status, 422)

    def test_create_expirations_201(self):
        """Test case for create with expirations query parameter 201 response code"""
        _, status, _ = self.api.create_with_http_info(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            expirations="",
            body=""
        )

        self.assertEqual(status, 201)

    def test_create_expirations_401(self):
        """Test case for create with expirations query parameter 401 response code"""
        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.create(
                self.account,
                "variable",
                TEST_VARIABLES[0],
                expirations="",
                body=""
            )

        self.assertEqual(context.exception.status, 401)

    def test_create_expirations_403(self):
        """Test case for create with expirations query parameter 403 response code"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.SecretsApi(alice_client)
        self.grant_insufficient_permissions()

        with self.assertRaises(conjur.ApiException) as context:
            alice_api.create(
                self.account,
                "variable",
                TEST_VARIABLES[0],
                expirations="",
                body=""
            )

        self.assertEqual(context.exception.status, 403)

    def test_create_expirations_404(self):
        """Test case for create with expirations query parameter 404 response code"""
        with self.assertRaises(conjur.ApiException) as context:
            self.api.create(
                self.account,
                "variable",
                'nonexist',
                expirations="",
                body=""
            )

        self.assertEqual(context.exception.status, 404)

    def test_show_version_200(self):
        """Test case for show 200 response with version parameter

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        response = self.api.show_with_http_info(
            self.account,
            "variable",
            TEST_VARIABLES[0],
            version='2'
        )
        self.assertEqual(secret_val, response[0])
        self.assertEqual(response[1], 200)

    def test_show_200(self):
        """Test case for show 200 response

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        response = self.api.show_with_http_info(self.account, "variable", TEST_VARIABLES[0])
        self.assertEqual(secret_val, response[0])
        self.assertEqual(response[1], 200)

    def test_show_401(self):
        """Test case for show 401 response with version parameter

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.show(self.account, "variable", TEST_VARIABLES[0], version=1)

        self.assertEqual(context.exception.status, 401)

    def test_show_version_401(self):
        """Test case for show 401 response"""
        secret_val = "secret data"
        self.api.create(self.account, "variable", TEST_VARIABLES[0], body=secret_val)

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.show(self.account, "variable", TEST_VARIABLES[0])

        self.assertEqual(context.exception.status, 401)

    def test_show_403(self):
        """Test case for show 403 response"""
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.SecretsApi(alice_client)
        self.grant_insufficient_permissions()

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            alice_api.show(self.account, "variable", TEST_VARIABLES[0])

        self.assertEqual(context.exception.status, 403)

    def test_show_404(self):
        """Test case for show 404 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.show(self.account, "variable", "badname")

        self.assertEqual(context.exception.status, 404)

    def test_show_422(self):
        """Test case for show 422 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.show(self.account, "variable", TEST_VARIABLES[0], version='')

        self.assertEqual(context.exception.status, 422)

    def test_show_batch_200(self):
        """Test case for show_batch 200 response

        Fetch multiple secrets
        """
        secret_values = ['one', 'two']
        for secret, value in zip(TEST_VARIABLES, secret_values):
            self.api.create(self.account, "variable", secret, body=value)

        # Secrets have to be in the format org:variable:secret_name
        secret_list = [f"dev:variable:{i}" for i in TEST_VARIABLES]
        response, status, _ = self.api.show_batch_with_http_info(
            ",".join(secret_list)
        )

        self.assertEqual(status, 200)
        for secret, value in zip(secret_list, secret_values):
            self.assertIn(secret, response)
            self.assertEqual(response[secret], value)

    def test_show_batch_401(self):
        """Test case for show_batch 401 response"""
        secret_list = ','.join([f"dev:variable:{i}" for i in TEST_VARIABLES])

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.show_batch(secret_list)

        self.assertEqual(context.exception.status, 401)

    def test_show_batch_403(self):
        """Test case for show_batch 403 response"""
        self.grant_insufficient_permissions()
        alice_client = api_config.get_api_client(username='alice')
        alice_api = conjur.api.SecretsApi(alice_client)
        secret_list = ','.join([f"dev:variable:{i}" for i in TEST_VARIABLES])

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            alice_api.show_batch(secret_list)

        self.assertEqual(context.exception.status, 403)

    def test_show_batch_404(self):
        """Test case for show_batch 404 response"""
        secret_list = f'{self.account}:variable:nonexist'

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.show_batch(secret_list)

        self.assertEqual(context.exception.status, 404)

    def test_show_batch_422(self):
        """Test case for show_batch 422 response"""
        secret_list = "\00"

        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.show_batch(secret_list)

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
