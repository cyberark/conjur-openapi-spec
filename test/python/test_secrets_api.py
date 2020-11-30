from __future__ import absolute_import

import unittest
import os

import openapi_client

from . import api_config
from .api_config import CONJUR_ACCOUNT

TEST_VARIABLES = ["one/password", "testSecret"]


class TestSecretsApi(unittest.TestCase):
    """SecretsApi unit test stubs"""
    @classmethod
    def setUpClass(cls):
        cls.account = os.environ[CONJUR_ACCOUNT]

        cls.client = api_config.get_api_client()

    def setUp(self):
        self.api = openapi_client.api.secrets_api.SecretsApi(self.client)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_create_variable(self):
        """Test case for create_variable

        Creates a secret value within the specified variable.
        """
        secret_val = "this is a secret"

        self.api.create_variable(self.account, "variable", TEST_VARIABLES[0], secret_val)

    def test_get_variable(self):
        """Test case for get_variable

        Fetches the value of a secret from the specified Variable.
        """
        secret_val = "secret data"
        self.api.create_variable(self.account, "variable", TEST_VARIABLES[0], secret_val)

        response = self.api.get_variable(self.account, "variable", TEST_VARIABLES[0])
        self.assertEqual(secret_val, response)

        secret_val = "new value"
        self.api.create_variable(self.account, "variable", TEST_VARIABLES[0], secret_val)

        response = self.api.get_variable(self.account, "variable", TEST_VARIABLES[0])
        self.assertEqual(secret_val, response)

    def test_get_variables(self):
        """Test case for get_variables

        Fetch multiple secrets
        """
        secret_values = ['one', 'two']
        for secret, value in zip(TEST_VARIABLES, secret_values):
            self.api.create_variable(self.account, "variable", secret, value)

        # Secrets have to be in the format org:variable:secret_name
        secret_list = [f"dev:variable:{i}" for i in TEST_VARIABLES]
        response = self.api.get_variables(",".join(secret_list))

        for secret, value in zip(secret_list, secret_values):
            self.assertIn(secret, response)
            self.assertEqual(response[secret], value)

if __name__ == '__main__':
    unittest.main()
