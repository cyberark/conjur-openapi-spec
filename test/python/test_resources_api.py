from __future__ import absolute_import

import unittest

from conjur import ApiException
from conjur.api import ResourcesApi
from conjur.models import Resource

from . import api_config

RESOURCE_MEMBERS = ['created_at', 'id', 'owner']

NULL_BYTE = '\00'

def authenticated_client_without_privilege():
    """Create and authenticate Alice, a user with no resource permissions
    Returns a Resource API client configured around Alice
    This is used in testing 404 responses due to lack of privilege
    """
    alice_client = api_config.get_api_client(username='alice')

    return ResourcesApi(alice_client)


class TestResourcesApi(api_config.ConfiguredTest):
    """ResourcesApi unit test stubs"""
    def setUp(self):
        self.api = ResourcesApi(self.client)
        self.bad_auth_api = ResourcesApi(self.bad_auth_client)

    # Test cases for /resources endpoint

    def test_show_resources_for_all_accounts_200(self):
        """Test case for 200 status response on /resources endpoint
        200 - successful, resources returned as JSON
        """
        response = self.api.show_resources_for_all_accounts_with_http_info()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        for resource in response.data:
            self.assertIsInstance(resource, Resource)
            for member in RESOURCE_MEMBERS:
                self.assertIsNotNone(getattr(resource, member))

    def test_show_resources_for_all_accounts_401(self):
        """Test case for 401 status response on /resources endpoint
        401 - unauthorized request
        """
        with self.assertRaises(ApiException) as context:
            self.bad_auth_api.show_resources_for_all_accounts()

        self.assertEqual(context.exception.status, 401)

    def test_show_resources_for_all_accounts_403(self):
        """Test case for 403 status response on /resources endpoint
        403 - the authenticated user lacks the necessary privilege
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resources_for_all_accounts(acting_as="user:alice")

        self.assertEqual(context.exception.status, 403)

    def test_show_resources_for_all_accounts_422(self):
        """Test case for 422 status response on /resources endpoint
        422 - Conjur received a malformed request parameter
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resources_for_all_accounts(account=NULL_BYTE)

        self.assertEqual(context.exception.status, 422)

    # Test cases for /resources/{account} endpoint

    def test_show_resources_for_account_200(self):
        """Test case for 200 status response on /resources/{account} endpoint
        200 - successful request, resources returned as JSON
        """
        response = self.api.show_resources_for_account_with_http_info(self.account)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        for resource in response.data:
            for member in RESOURCE_MEMBERS:
                self.assertIsNotNone(getattr(resource, member))

    def test_show_resources_for_account_400(self):
        """Test case for 400 status response on /resources/{account} endpoint
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resources_for_account(NULL_BYTE)

        self.assertEqual(context.exception.status, 400)

    def test_show_resources_for_account_401(self):
        """Test case for 401 status response on /resources/{account} endpoint
        401 - unauthorized request
        """
        with self.assertRaises(ApiException) as context:
            self.bad_auth_api.show_resources_for_account(self.account)

        self.assertEqual(context.exception.status, 401)

    def test_show_resources_for_account_403(self):
        """Test case for 403 status response on /resources/{account} endpoint
        403 - the authenticated user lacks the necessary privilege
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resources_for_account(self.account, acting_as="user:alice")

        self.assertEqual(context.exception.status, 403)

    def test_show_resources_for_account_422(self):
        """Test case for 422 status response on /resources/{account} endpoint
        422 - Conjur received a malformed request parameter
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resources_for_account(self.account, kind=NULL_BYTE)

        self.assertEqual(context.exception.status, 422)

    # Test cases for /resources/{account}/{kind} endpoint

    def test_show_resources_for_kind_200(self):
        """Test case for 200 status response on /resources/{account}/{kind}
        200 - successful request, resources returned as JSON
        """
        response = self.api.show_resources_for_kind_with_http_info(
            self.account,
            "policy"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        for resource in response.data:
            for member in RESOURCE_MEMBERS:
                self.assertIsNotNone(getattr(resource, member))

    def test_show_resources_for_kind_400(self):
        """Test case for 400 status response on /resources/{account}/{kind} endpoint
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resources_for_kind(NULL_BYTE, "variable")

        self.assertEqual(context.exception.status, 400)

    def test_show_resources_for_kind_401(self):
        """Test case for 401 status response on /resources/{account}/{kind} endpoint
        401 - unauthorized request
        """
        with self.assertRaises(ApiException) as context:
            self.bad_auth_api.show_resources_for_kind(self.account, "variable")

        self.assertEqual(context.exception.status, 401)

    def test_show_resources_for_kind_403(self):
        """Test case for 403 status response on /resources/{account}/{kind} endpoint
        403 - the authenticated user lacks the necessary privilege
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resources_for_kind(
                self.account,
                "variable",
                acting_as="user:alice"
            )

        self.assertEqual(context.exception.status, 403)

    def test_show_resources_for_kind_422(self):
        """Test case for 422 status response on /resources/{account}/{kind}
        422 - Conjur received a malformed request parameter
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resources_for_kind(self.account, "variable", search=NULL_BYTE)

        self.assertEqual(context.exception.status, 422)

    # Test cases for /resources/{account}/{kind}/{identifier} endpoint

    def test_show_resource_200(self):
        """Test case for 200 status response on /resources/{account}/{kind}/{identifier}
        200 - successful, role memberships returned as JSON
        """
        response = self.api.show_resource_with_http_info(
            self.account,
            'variable',
            'testSecret'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, Resource)
        for i in RESOURCE_MEMBERS:
            self.assertIsNotNone(getattr(response.data, i))

    def test_show_resource_204(self):
        """Test case for 204 status response on /resources/{account}/{kind}/{identifier}
        204 - permission check successful
        """
        response = self.api.show_resource_with_http_info(
            self.account,
            'variable',
            'testSecret',
            privilege="update",
            check=True
        )

        self.assertEqual(response.status_code, 204)
        self.assertIsNone(response.data)

    def test_show_resource_400(self):
        """Test case for 400 status response on /resources/{account}/{kind}/{identifier} endpoint
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resource(self.account, NULL_BYTE, 'testSecret')

        self.assertEqual(context.exception.status, 400)

    def test_show_resource_401(self):
        """Test case for 401 status response on /resources/{account}/{kind}/{identifier} endpoint
        401 - unauthorized request
        """
        with self.assertRaises(ApiException) as context:
            self.bad_auth_api.show_resource(self.account, 'variable', 'testSecret')

        self.assertEqual(context.exception.status, 401)

    def test_show_resource_403(self):
        """Test case for 403 status response on /resources/{account}/{kind}/{identifier} endpoint
        403 - the specified role does not have privilege over the resource
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resource(
                self.account,
                'variable',
                'testSecret',
                check=True,
                privilege='read',
                role='user:alice'
            )

        self.assertEqual(context.exception.status, 403)

    def test_show_resource_404a(self):
        """Test case for 404 status response on /resources/{account}/{kind}/{identifier} endpoint
        404 - the requested resource does not exist
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resource(self.account, 'variable', 'fakeVariable')

        self.assertEqual(context.exception.status, 404)

    def test_show_resource_404b(self):
        """Test case for 404 status response on /resources/{account}/{kind}/{identifier} endpoint
        404 - the authenticated user lacks the necessary privilege
        Conjur docs say this should return 403 - Conjur api feature tests say otherwise
        """
        alice_resource_api = authenticated_client_without_privilege()

        with self.assertRaises(ApiException) as context:
            alice_resource_api.show_resource(
                self.account,
                'variable',
                'testSecret'
            )

        self.assertEqual(context.exception.status, 404)

    # Python clients gen'd with the latest generator version are unable to
    # get a 404 response on this endpoint. The API now validates parameters
    # types as described by the OpenAPI description.
    @unittest.skip("Outdated")
    def test_show_resource_422(self):
        """Test case for 422 status response on /resources/{account}/{kind}/{identifier} endpoint
        422 - Conjur received a malformed request parameter
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_resource(
                self.account,
                'variable',
                'testSecret',
                check=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

    # Test combinations of optional query parameters when getting a single resource

    def test_permitted_roles_and_check(self):
        """Test case for using both `permitted_roles` and `check` query parameters
        When both parameters are used, Conjur responds to the `check` call only
        """
        response = self.api.show_resource_with_http_info(
            self.account,
            'variable',
            'testSecret',
            permitted_roles=True,
            check=True,
            privilege='read'
        )

        self.assertEqual(response.status_code, 204)
        self.assertIsNone(response.data)

if __name__ == '__main__':
    unittest.main()
