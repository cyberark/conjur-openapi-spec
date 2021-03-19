from __future__ import absolute_import

import unittest
import datetime

import openapi_client

from . import api_config

TEST_HOST = "testHost"
HOST_FACTORY = "dev:host_factory:testFactory"
FACTORY_POLICY = '''
- !layer testLayer
- !host_factory
    id: testFactory
    annotations:
        description: Testing factory
    layers: [ !layer testLayer ]
'''

HOST_TOKEN_MEMBERS = ['expiration', 'cidr', 'token']
NEW_HOST_MEMBERS = ['created_at',  'id', 'owner', 'api_key']

class TestHostFactoryApi(api_config.ConfiguredTest):
    """HostFactoryApi unit test stubs"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        policy_api = openapi_client.api.policies_api.PoliciesApi(cls.client)
        policy_api.update_policy(cls.account, 'root', FACTORY_POLICY)

    def setUp(self):
        self.api = openapi_client.api.host_factory_api.HostFactoryApi(self.client)

    def get_host_token(self):
        """Gets a token used for creating new hosts"""
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        token = self.api.create_host_token(tomorrow, HOST_FACTORY)
        return token[0]

    def test_create_host(self):
        """Test case for create_host

        Creates a Host using the Host Factory.
        """
        token = self.get_host_token()['token']

        old_key = dict(self.client.configuration.api_key)
        self.client.configuration.api_key = {'Authorization': f'Token token="{token}"'}
        new_host = self.api.create_host(TEST_HOST)
        self.client.configuration.api_key = old_key

        # Ensure the return object has the correct members
        self.assertIsInstance(new_host, dict)
        for member in NEW_HOST_MEMBERS:
            self.assertIn(member, new_host)

        # Make sure the new host can authenticate
        authn = openapi_client.api.AuthenticationApi(self.client)
        authn.get_access_token(
            self.account,
            f'host/{TEST_HOST}',
            body=new_host['api_key']
        )

    def test_create_host_token(self):
        """Test case for create_host_token

        Creates one or more host identity tokens.
        """
        token = self.get_host_token()

        self.assertIsInstance(token, dict)
        for i in HOST_TOKEN_MEMBERS:
            self.assertIn(i, token)

    def test_revoke_host_token(self):
        """Test case for revoke_host_token

        Revokes a token, immediately disabling it.
        """
        token = self.get_host_token()['token']

        old_key = dict(self.client.configuration.api_key)

        self.api.revoke_host_token(token)

        self.client.configuration.api_key = {'Authorization': f'Token token="{token}"'}

        with self.assertRaises(openapi_client.exceptions.ApiException):
            self.api.create_host(TEST_HOST)

        self.client.configuration.api_key = old_key

if __name__ == '__main__':
    unittest.main()
