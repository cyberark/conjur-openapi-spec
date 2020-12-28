from __future__ import absolute_import

import unittest

import openapi_client

from . import api_config

RESOURCE_MEMBERS = ['created_at', 'id', 'owner']

POLICY_ALICE = "- !user alice"

NULL_BYTE = '\00'

class TestResourcesApi(api_config.ConfiguredTest):
    """ResourcesApi unit test stubs"""
    def setUp(self):
        self.api = openapi_client.api.resources_api.ResourcesApi(self.client)
        self.bad_auth_api = openapi_client.api.resources_api.ResourcesApi(self.bad_auth_client)

    def authenticated_client_without_privilege(self):
        """Create and authenticate Alice, a user with no resource permissions
        Returns a Resource API client configured around Alice
        This is used in testing 404 responses due to lack of privilege
        """
        policy_api = openapi_client.PoliciesApi(self.client)

        alice_info = policy_api.modify_policy(self.account, 'root', POLICY_ALICE)
        alice_api_key = alice_info["created_roles"]["dev:user:alice"]["api_key"]

        config = api_config.get_api_config()
        config.username = "alice"
        alice_client = openapi_client.ApiClient(config)
        authn_api = openapi_client.AuthnApi(alice_client)
        alice_authn_token = authn_api.authenticate(
            self.account,
            config.username,
            alice_api_key,
            accept_encoding='base64'
        )
        alice_client.configuration.api_key = {'Authorization': f'Token token="{alice_authn_token}"'}

        return openapi_client.ResourcesApi(alice_client)

    # Test cases for /resources endpoint

    def test_get_resources_200(self):
        """Test case for 200 status response on /resources endpoint
        200 - successful, resources returned as JSON
        """
        response = self.api.get_resources_with_http_info()

        self.assertEqual(response[1], 200)
        self.assertIsInstance(response[0], list)
        for resource in response[0]:
            for member in RESOURCE_MEMBERS:
                self.assertIn(member, resource)

    def test_get_resources_401(self):
        """Test case for 401 status response on /resources endpoint
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.get_resources()

        self.assertEqual(context.exception.status, 401)

    def test_get_resources_403(self):
        """Test case for 403 status response on /resources endpoint
        403 - the authenticated user lacks the necessary privilege
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_resources(acting_as="user:alice")

        self.assertEqual(context.exception.status, 403)

    def test_get_resources_422(self):
        """Test case for 422 status response on /resources endpoint
        422 - an optional query parameter is malformed
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_resources(account=NULL_BYTE)

        self.assertEqual(context.exception.status, 422)

    # Test cases for /resources/{account} endpoint

    def test_get_resources_on_account_200(self):
        """Test case for 200 status response on /resources/{account} endpoint
        200 - successful request, resources returned as JSON
        """
        response = self.api.get_resources_on_account_with_http_info(self.account)

        self.assertEqual(response[1], 200)
        self.assertIsInstance(response[0], list)
        for resource in response[0]:
            for member in RESOURCE_MEMBERS:
                self.assertIn(member, resource)

    def test_get_resources_on_account_400(self):
        """Test case for 400 status response on /resources/{account} endpoint
        400 - a required URI parameter is malformed
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_resources_on_account(NULL_BYTE)

        self.assertEqual(context.exception.status, 400)

    def test_get_resources_on_account_401(self):
        """Test case for 401 status response on /resources/{account} endpoint
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.get_resources_on_account(self.account)

        self.assertEqual(context.exception.status, 401)

    def test_get_resources_on_account_403(self):
        """Test case for 403 status response on /resources/{account} endpoint
        403 - the authenticated user lacks the necessary privilege
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_resources_on_account(self.account, acting_as="user:alice")

        self.assertEqual(context.exception.status, 403)

    def test_get_resources_on_account_422(self):
        """Test case for 422 status response on /resources/{account} endpoint
        422 - an optional query parameter is malformed
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_resources_on_account(self.account, kind=NULL_BYTE)

        self.assertEqual(context.exception.status, 422)

    # Test cases for /resources/{account}/{kind} endpoint

    def test_get_similar_resources_on_account_200(self):
        """Test case for 200 status response on /resources/{account}/{kind}
        200 - successful request, resources returned as JSON
        """
        response = self.api.get_similar_resources_on_account_with_http_info(
            self.account,
            "variable"
        )

        self.assertEqual(response[1], 200)
        self.assertIsInstance(response[0], list)
        for resource in response[0]:
            for member in RESOURCE_MEMBERS:
                self.assertIn(member, resource)

    def test_get_similar_resources_on_account_400(self):
        """Test case for 400 status response on /resources/{account}/{kind} endpoint
        400 - a required URI parameter is malformed
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_similar_resources_on_account(NULL_BYTE, "variable")

        self.assertEqual(context.exception.status, 400)

    def test_get_similar_resources_on_account_401(self):
        """Test case for 401 status response on /resources/{account}/{kind} endpoint
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.get_similar_resources_on_account(self.account, "variable")

        self.assertEqual(context.exception.status, 401)

    def test_get_similar_resources_on_account_403(self):
        """Test case for 403 status response on /resources/{account}/{kind} endpoint
        403 - the authenticated user lacks the necessary privilege
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_similar_resources_on_account(
                self.account,
                "variable",
                acting_as="user:alice"
            )

        self.assertEqual(context.exception.status, 403)

    def test_get_similar_resources_on_account_422(self):
        """Test case for 422 status response on /resources/{account}/{kind}
        422 - on optional query parameter is malformed
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_similar_resources_on_account(self.account, "variable", search=NULL_BYTE)

        self.assertEqual(context.exception.status, 422)

    # Test cases for /resources/{account}/{kind}/{identifier} endpoint

    def test_get_resource_200(self):
        """Test case for 200 status response on /resources/{account}/{kind}/{identifier}
        200 - successful, role memberships returned as JSON
        """
        response = self.api.get_resource_with_http_info(
            self.account,
            'variable',
            'testSecret'
        )

        self.assertEqual(response[1], 200)
        self.assertIsInstance(response[0], dict)
        for i in RESOURCE_MEMBERS:
            self.assertIn(i, response[0])

    def test_get_resource_204(self):
        """Test case for 204 status response on /resources/{account}/{kind}/{identifier}
        204 - permission check successful
        """
        response = self.api.get_resource_with_http_info(
            self.account,
            'variable',
            'testSecret',
            privilege="update",
            check=True
        )
        self.assertEqual(response[1], 204)
        self.assertEqual(response[0], "")

    def test_get_resource_400(self):
        """Test case for 400 status response on /resources/{account}/{kind}/{identifier} endpoint
        400 - a required URI parameter is malformed
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_resource(self.account, NULL_BYTE, 'testSecret')

        self.assertEqual(context.exception.status, 400)

    def test_get_resource_401(self):
        """Test case for 401 status response on /resources/{account}/{kind}/{identifier} endpoint
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.get_resource(self.account, 'variable', 'testSecret')

        self.assertEqual(context.exception.status, 401)

    def test_get_resource_404a(self):
        """Test case for 404 status response on /resources/{account}/{kind}/{identifier} endpoint
        404 - the requested resource does not exist
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_resource(self.account, 'variable', 'fakeVariable')

        self.assertEqual(context.exception.status, 404)

    def test_get_resource_404b(self):
        """Test case for 404 status response on /resources/{account}/{kind}/{identifier} endpoint
        404 - the authenticated user lacks the necessary privilege
        Conjur docs say this should return 403 - Conjur api feature tests say otherwise
        """
        alice_resource_api = self.authenticated_client_without_privilege()

        with self.assertRaises(openapi_client.ApiException) as context:
            alice_resource_api.get_resource_with_http_info(self.account, 'variable', 'testSecret')

        self.assertEqual(context.exception.status, 404)

    def test_get_resource_422(self):
        """Test case for 422 status response on /resources/{account}/{kind}/{identifier} endpoint
        422 - an optional query parameter is malformed
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_resource(self.account, 'variable', 'testSecret', check=NULL_BYTE)

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
