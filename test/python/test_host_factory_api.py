from __future__ import absolute_import

import unittest
import datetime

import conjur

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

class TestHostFactoryApi(api_config.ConfiguredTest):
    """HostFactoryApi unit test stubs"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        policy_api = conjur.api.policies_api.PoliciesApi(cls.client)
        policy_api.load_policy(cls.account, 'root', FACTORY_POLICY)

    def setUp(self):
        self.api = conjur.api.host_factory_api.HostFactoryApi(self.client)

    def get_host_token(self):
        """Gets a token used for creating new hosts"""
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        token = self.api.create_token(tomorrow, HOST_FACTORY)
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
        self.assertIsInstance(new_host, conjur.models.CreateHost)

        # Make sure the new host can authenticate
        authn = conjur.api.AuthenticationApi(self.client)
        authn.get_access_token(
            self.account,
            f'host/{TEST_HOST}',
            body=new_host.api_key
        )

    def test_create_token(self):
        """Test case for create_token

        Creates one or more host identity tokens.
        """
        token = self.get_host_token()

        self.assertIsInstance(token, dict)
        for i in HOST_TOKEN_MEMBERS:
            self.assertIn(i, token)

    def test_revoke_token(self):
        """Test case for revoke_token

        Revokes a token, immediately disabling it.
        """
        token = self.get_host_token()['token']

        old_key = dict(self.client.configuration.api_key)

        self.api.revoke_token(token)

        self.client.configuration.api_key = {'Authorization': f'Token token="{token}"'}

        with self.assertRaises(conjur.exceptions.ApiException):
            self.api.create_host(TEST_HOST)

        self.client.configuration.api_key = old_key

if __name__ == '__main__':
    unittest.main()
