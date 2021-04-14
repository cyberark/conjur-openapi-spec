from __future__ import absolute_import

import unittest
import datetime
import os

import conjur

from . import api_config

TEST_HOST = "testHost"
HOST_FACTORY = f"{os.environ.get(api_config.CONJUR_ACCOUNT)}:host_factory:testFactory"
FACTORY_POLICY = '''
- !layer testLayer
- !host_factory
    id: testFactory
    annotations:
        description: Testing factory
    layers: [ !layer testLayer ]

- !user carl
- !permit
  role: !user carl
  privileges: [ read ]
  resource: !host_factory testFactory
'''

HOST_TOKEN_MEMBERS = ['expiration', 'cidr', 'token']
EXPIRE = datetime.date.today() + datetime.timedelta(days=1)

class TestHostFactoryApi(api_config.ConfiguredTest):
    """HostFactoryApi unit test stubs"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        policy_api = conjur.PoliciesApi(cls.client)
        policy_api.load_policy(cls.account, 'root', FACTORY_POLICY)

    def setUp(self):
        self.api = conjur.HostFactoryApi(self.client)
        self.bad_auth_api = conjur.HostFactoryApi(self.bad_auth_client)

    def get_host_token(self):
        """Gets a token used for creating new hosts"""
        token = self.api.create_token(EXPIRE, HOST_FACTORY)
        return token[0]['token']

    # test cases for conjur.HostFactoryApi.create_host

    def test_create_host_201(self):
        """Test case for 201 response when creating a host
        Creates a Host using the Host Factory.
        """
        token = self.get_host_token()
        old_key = dict(self.client.configuration.api_key)
        self.client.configuration.api_key = {'Authorization': f'Token token="{token}"'}

        new_host, status, _ = self.api.create_host_with_http_info(TEST_HOST)
        self.assertEqual(status, 201)
        self.assertIsInstance(new_host, conjur.models.CreateHost)

        # Make sure the new host can authenticate
        authn = conjur.api.AuthenticationApi(self.client)
        authn.get_access_token(
            self.account,
            f'host/{TEST_HOST}',
            body=new_host.api_key
        )

        self.client.configuration.api_key = old_key

    def test_create_host_401(self):
        """Test case for 401 response when creating a host
        401 - Unauthorized request
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.create_host(TEST_HOST)

        self.assertEqual(context.exception.status, 401)

    def test_create_host_422(self):
        """Test case for 422 response when creating a host
        This response occurs when the ID parameter is empty
        """
        token = self.get_host_token()
        old_key = dict(self.client.configuration.api_key)
        self.client.configuration.api_key = {'Authorization': f'Token token="{token}"'}

        with self.assertRaises(conjur.ApiException) as context:
            self.api.create_host("")
        self.assertEqual(context.exception.status, 422)

        self.client.configuration.api_key = old_key

    # test cases for conjur.HostFactoryAPI.create_host_token

    def test_create_token_200(self):
        """Test case for 200 response when creating a host token
        Creates one or more host identity tokens.
        """
        token_data_list, response, _ = self.api.create_token_with_http_info(
            EXPIRE,
            HOST_FACTORY
        )
        token_data = token_data_list[0]

        self.assertEqual(response, 200)
        self.assertIsInstance(token_data, dict)
        for i in HOST_TOKEN_MEMBERS:
            self.assertIn(i, token_data)

    def test_create_token_401(self):
        """Test case for 401 response when creating a host token
        401 - Unauthorized request
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.create_token(EXPIRE, HOST_FACTORY)

        self.assertEqual(context.exception.status, 401)

    def test_create_token_403(self):
        """Test case for 403 response when creating a host token
        403 - Inadequate privileges
        The requesting role requires `execute` privilege on the Host Factory
        """
        no_exec_client = api_config.get_api_client('carl')
        no_exec_api = conjur.HostFactoryApi(no_exec_client)

        with self.assertRaises(conjur.ApiException) as context:
            no_exec_api.create_token(EXPIRE, HOST_FACTORY)

        self.assertEqual(context.exception.status, 403)

    def test_create_token_404(self):
        """Test case for 404 response when creating a host token
        404 - the requested host factory does not exist
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.create_token(EXPIRE, "fake_factory")

        self.assertEqual(context.exception.status, 404)

    def test_create_token_422(self):
        """Test case for 422 response when creating a host token
        422 - Unprocessable entity
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.create_token('fake_date', HOST_FACTORY)

        self.assertEqual(context.exception.status, 422)

    # test cases for conjur.HostFactoryAPI.revoke_host_token

    def test_revoke_token_204(self):
        """Test case for 204 response when revoking a host token
        Revokes a token, immediately disabling it.
        """
        token = self.get_host_token()
        old_key = dict(self.client.configuration.api_key)

        _, status, _ = self.api.revoke_token_with_http_info(token)
        self.assertEqual(status, 204)

        self.client.configuration.api_key = {'Authorization': f'Token token="{token}"'}
        with self.assertRaises(conjur.exceptions.ApiException):
            self.api.create_host(TEST_HOST)

        self.client.configuration.api_key = old_key

    def test_revoke_token_400(self):
        """Test case for 400 response when revoking a host token
        400 - Bad request
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.revoke_token('\00')

        self.assertEqual(context.exception.status, 400)

    def test_revoke_token_401(self):
        """Test case for 401 response when revoking a host token
        401 - Unauthorized request
        """
        token = self.get_host_token()
        old_key = dict(self.client.configuration.api_key)

        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.revoke_token(token)

        self.assertEqual(context.exception.status, 401)
        self.client.configuration.api_key = old_key

    def test_revoke_token_404(self):
        """Test case for 404 response when revoking a host token
        404 - Conjur did not find the specified token
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.revoke_token("fake_token")

        self.assertEqual(context.exception.status, 404)

if __name__ == '__main__':
    unittest.main()
