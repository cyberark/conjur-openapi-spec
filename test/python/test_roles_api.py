from __future__ import absolute_import

import unittest

import openapi_client

from . import api_config

ROLES_POLICY = """
- !group
  id: userGroup
  annotations:
    editable: true

- !user bob
- !user alice
"""

NULL_BYTE = '\00'

class TestRolesApi(api_config.ConfiguredTest):
    """RolesApi unit test stubs"""
    def setUp(self):
        self.api = openapi_client.RolesApi(self.client)
        self.bad_auth_api = openapi_client.RolesApi(self.bad_auth_client)

        # set a new root policy including a new group and an unrelated user
        # the group/user pair will be used to test member addition and deletion
        # along with lists of role members and memberships
        policy_api = openapi_client.PoliciesApi(self.client)
        # this policy discards the policy load and member assignments from the previous test case
        policy_api.load_policy(self.account, 'root', ROLES_POLICY)

    def tearDown(self):
        default_policy = api_config.get_default_policy()
        policy_api = openapi_client.api.policies_api.PoliciesApi(self.client)
        policy_api.load_policy(self.account, 'root', default_policy)

    def add_user_to_group(self, identifier):
        """Adds a given user to the group defined in the ROLES_POLICY
        """
        role_id = self.account + ":user:" + identifier
        response = self.api.add_member_with_http_info(
            self.account,
            'group',
            'userGroup',
            members="",
            member=role_id
        )
        return response

    # Test cases for GET requests to /roles/{account}/{kind}/{identifier} endpoint

    def test_get_role_200(self):
        """Test case for get_role

        Get role information
        """
        response = self.api.get_role_with_http_info(self.account, 'user', 'admin')
        role_details = response[0]

        self.assertEqual(response[1], 200)
        self.assertIsInstance(role_details, dict)
        members = ['created_at', 'id', 'members']
        for i in members:
            self.assertIn(i, role_details)

    def test_get_role_400(self):
        """Test case for 400 status repsonse on /roles/{account}/{kind}/{identifier} endpoint
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role_with_http_info(self.account, NULL_BYTE, 'admin')

        self.assertEqual(context.exception.status, 400)

    def test_get_role_401(self):
        """Test case for 401 status response on /roles/{account}/{kind}/{identifier} endpoint
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.get_role_with_http_info(self.account, 'user', 'admin')

        self.assertEqual(context.exception.status, 401)

    def test_get_role_403(self):
        """Test case for 403 status response on /roles/{account}/{kind}/{identifier} endpoint
        403 - the authenticated user lacks the required privilege
        """
        # establish a new api client as user Alice
        alice_client = api_config.get_api_client(username="alice")
        alice_roles_api = openapi_client.RolesApi(alice_client)

        # attempt to show group:userGroup's role details
        with self.assertRaises(openapi_client.ApiException) as context:
            response = alice_roles_api.get_role_with_http_info(
                self.account,
                'user',
                'bob'
            )
            print(response)

        self.assertEqual(context.exception.status, 403)

    def test_get_role_404(self):
        """Test case for 404 status response on /roles/{account}/{kind}/{identifier} endpoint
        404 - the role could not be found
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role_with_http_info(self.account, 'user', 'fakeUser')

        self.assertEqual(context.exception.status, 404)

    def test_get_role_422(self):
        """Test case for 422 status response on /roles/{account}/{kind}/{identifier} endpoint
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role_with_http_info(
                self.account,
                'user',
                'admin',
                members="",
                search=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

    # Test query parameters on GET requests to /roles/{account}/{kind}/{identifier} endpoint

    def test_get_members(self):
        """Test using members query parameter on GET requests
        Queries group:userGroup role for its members, which should only be dev:user:admin
        """
        response = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members=""
        )

        target_response = [
            {
                'admin_option': True,
                'ownership': True,
                'role': 'dev:group:userGroup',
                'member': 'dev:user:admin',
                'policy': 'dev:policy:root'
            }
        ]

        self.assertEqual(response, target_response)

    def test_get_members_count(self):
        """Test using members & count query parameters on GET
        Adds dev:user:bob as a member of group:userGroup, then queries for a member count
        """
        self.add_user_to_group("bob")
        self.add_user_to_group("alice")

        response = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members="",
            count=True
        )

        self.assertEqual(response['count'], 3)

    def test_get_members_offset(self):
        """Test using members & offset query parameters on GET requests
        Returns member data starting at <offset>
        """
        self.add_user_to_group("bob")
        self.add_user_to_group("alice")

        response = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members="",
            offset=2
        )

        # starting at offset 2 should omit user:admin (0) and user:alice (1)
        target_response = [
            {
                'admin_option': False,
                'ownership': False,
                'role': 'dev:group:userGroup',
                'member': 'dev:user:bob'
            }
        ]

        self.assertEqual(response, target_response)

    def test_get_members_limit(self):
        """Test using members & limit query parameters on GET requests
        Returns member data limited to the first <limit> results
        """
        self.add_user_to_group("bob")
        self.add_user_to_group("alice")

        response = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members="",
            limit=2
        )

        # limiting the results to the first 2 should omit user:bob (idx 2)
        target_response = [
            {
                'admin_option': True,
                'ownership': True,
                'role': 'dev:group:userGroup',
                'member': 'dev:user:admin',
                'policy': 'dev:policy:root'
            },
            {
                'admin_option': False,
                'ownership': False,
                'role': 'dev:group:userGroup',
                'member': 'dev:user:alice'
            }
        ]

        self.assertEqual(response, target_response)

    # Test cases for POST requests to /roles/{account}/{kind}/{identifier}?members&member="{role}"

    def test_add_members_204(self):
        """Test case for 204 status response
        This endpoint will assign a given role as a member to another role
        The example shown here is a user Bob being assigned as a member of a group
        204 - successful member assignment, empty response body
        """
        response = self.add_user_to_group("bob")
        self.assertEqual(response[1], 204)

        group_member_data = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members=""
        )

        self.assertEqual(len(group_member_data), 2)
        members = ["dev:user:admin", "dev:user:bob"]
        for i in range(0, 2):
            self.assertEqual(group_member_data[i]['member'], members[i])

    def test_add_members_400(self):
        """Test case for 400 status response
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.add_member_with_http_info(
                self.account,
                NULL_BYTE,
                'userGroup',
                members="",
                member='dev:user:bob'
            )

        self.assertEqual(context.exception.status, 400)

    def test_add_members_401(self):
        """Test case for 401 status response
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.add_member_with_http_info(
                self.account,
                'group',
                'userGroup',
                members="",
                member='dev:user:bob'
            )

        self.assertEqual(context.exception.status, 401)

    def test_add_members_403(self):
        """Test case for 403 status response
        403 - the authenticated user lacks the necessary privilege
        """
        # establish a new api client as user Bob
        bob_client = api_config.get_api_client(username="bob")
        bob_roles_api = openapi_client.RolesApi(bob_client)

        # attempt to add bob as member of userGroup as bob himself
        with self.assertRaises(openapi_client.ApiException) as context:
            bob_roles_api.add_member_with_http_info(
                self.account,
                'group',
                'userGroup',
                members="",
                member='dev:user:bob'
            )

        self.assertEqual(context.exception.status, 403)

    def test_add_members_404(self):
        """Test case for 404 status response
        404 - the queried role inteded for assignment as member does not exist
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.add_member_with_http_info(
                self.account,
                'group',
                'userGroup',
                members="",
                member='dev:user:fakeUser'
            )

        self.assertEqual(context.exception.status, 404)

    def test_add_members_422(self):
        """Test case for 422 status response
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.add_member_with_http_info(
                self.account,
                'group',
                'userGroup',
                members="",
                member=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
