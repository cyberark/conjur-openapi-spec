from __future__ import absolute_import

import unittest

import openapi_client

import api_config

NEW_VARIABLE = 'policy/test'

TEST_POLICY = f'''
- !variable one/password
- !variable testSecret
- !variable {NEW_VARIABLE}
'''

MODIFY_POLICY = f'''
- !delete
  record: !variable {NEW_VARIABLE}
'''

UPDATE_POLICY = f'''
- !variable {NEW_VARIABLE}
'''

class TestPoliciesApi(api_config.ConfiguredTest):
    """PoliciesApi unit test stubs"""
    def setUp(self):
        self.api = openapi_client.api.policies_api.PoliciesApi(self.client)

    def test_load_policy(self):
        """Test case for load_policy

        Loads or replaces a Conjur policy document.
        """
        self.api.load_policy(self.account, 'root', TEST_POLICY)

        # Sanity check, make sure the new variable is accessable
        secrets = openapi_client.api.secrets_api.SecretsApi(self.client)
        secrets.create_variable(self.account, 'variable', NEW_VARIABLE, 'random_data')

    def test_modify_policy(self):
        """Test case for modify_policy

        Modifies an existing Conjur policy.
        """
        self.api.modify_policy(self.account, 'root', MODIFY_POLICY)

        # make sure the delete went through
        secrets = openapi_client.api.secrets_api.SecretsApi(self.client)

        with self.assertRaises(openapi_client.exceptions.ApiException):
            secrets.get_variable(self.account, 'variable', NEW_VARIABLE)

    def test_update_policy(self):
        """Test case for update_policy

        Adds data to the existing Conjur policy.
        """
        self.api.update_policy(self.account, 'root', UPDATE_POLICY)

        # Test that we can set the new secret
        secrets = openapi_client.api.secrets_api.SecretsApi(self.client)
        secret_val = 'new secret value'

        secrets.create_variable(self.account, 'variable', NEW_VARIABLE, secret_val)

if __name__ == '__main__':
    unittest.main()
