from __future__ import absolute_import

import unittest

import openapi_client

import api_config

ROLES_POLICY = """
- !layer testLayer

- !group
  id: userGroup
  annotations:
    editable: true

- !group
  id: anotherGroup
  annotations:
    editable: true

- !user bob
- !user alice
"""

NULL_BYTE = '\00'

class TestRolesApi(api_config.ConfiguredTest):
    """RolesApi unit test stubs"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ADMIN_ID = f'{cls.account}:user:admin'
        cls.ALICE_ID = f'{cls.account}:user:alice'
        cls.BOB_ID   = f'{cls.account}:user:bob'
        cls.GROUP_ID = f'{cls.account}:group:userGroup'
        cls.ROOT_ID  = f'{cls.account}:policy:root'

    def setUp(self):
        self.api = openapi_client.RolesApi(self.client)
        self.bad_auth_api = openapi_client.RolesApi(self.bad_auth_client)

        # set a new root policy including a new group and users Alice and Bob
        # these will be used to test member addition/deletion
        policy_api = openapi_client.PoliciesApi(self.client)
        policy_api.load_policy(self.account, 'root', ROLES_POLICY)

    def tearDown(self):
        super().load_default_policy()

    def add_user_to_group(self, identifier):
        """Adds a given user to the group defined in ROLES_POLICY
        """
        role_id = f'{self.account}:user:{identifier}'
        response = self.api.add_member_with_http_info(
            self.account,
            'group',
            'userGroup',
            members='',
            member=role_id
        )
        return response

    # Test cases for GET requests to /roles/{account}/{kind}/{identifier} endpoint

    def test_get_role_200(self):
        """Test case for 200 status response when getting role data
        Gets information on the specified role
        """
        role_details, status, _ = self.api.get_role_with_http_info(self.account, 'user', 'admin')

        self.assertEqual(status, 200)
        self.assertIsInstance(role_details, dict)
        members = ['created_at', 'id', 'members']
        for i in members:
            self.assertIn(i, role_details)

    def test_get_role_400(self):
        """Test case for 400 status repsonse when getting role data
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(self.account, NULL_BYTE, 'admin')

        self.assertEqual(context.exception.status, 400)

    def test_get_role_401(self):
        """Test case for 401 status response when getting role data
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.get_role(self.account, 'user', 'admin')

        self.assertEqual(context.exception.status, 401)

    def test_get_role_404(self):
        """Test case for 404 status response when getting role data
        404 - the role could not be found
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(self.account, 'user', 'fakeUser')

        self.assertEqual(context.exception.status, 404)

    def test_get_role_422(self):
        """Test case for 422 status response when getting role data
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(
                self.account,
                'user',
                'admin',
                members='',
                search=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

    # Test cases for getting all of a role's memberships, expanded recursively

    def test_get_all_memberships_200(self):
        """Test case for 200 status response for GET requests using 'all' query parameter
        Queries user:bob for all its memberships, expanded recursively
        """
        # Set bob as member of userGroup and anotherGroup
        # Set userGroup as member of testLayer
        self.add_user_to_group('bob')

        self.api.add_member(
            self.account,
            'group',
            'anotherGroup',
            members='',
            member=self.BOB_ID
        )

        self.api.add_member(
            self.account,
            'layer',
            'testLayer',
            members='',
            member=self.GROUP_ID
        )

        # testLayer will be listed in all memberships of bob
        bob_membership_data, status, _ = self.api.get_role_with_http_info(
            self.account,
            'user',
            'bob',
            all=''
        )

        target_membership_data = [
            f'{self.account}:layer:testLayer',
            f'{self.account}:group:anotherGroup',
            f'{self.account}:group:userGroup',
            f'{self.account}:user:bob'
        ]

        self.assertEqual(status, 200)
        self.assertEqual(bob_membership_data, target_membership_data)

    def test_get_all_memberships_400(self):
        """Test case for 400 status response for GET requests using 'all' query parameter
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(
                self.account,
                NULL_BYTE,
                'admin',
                all=''
            )

        self.assertEqual(context.exception.status, 400)

    def test_get_all_memberships_401(self):
        """Test case for 401 status response for GET requests using 'all' query parameter
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.get_role(
                self.account,
                'user',
                'admin',
                all=''
            )

        self.assertEqual(context.exception.status, 401)

    def test_get_all_memberships_404(self):
        """Test case for 404 status response for GET requests using 'all' query parameter
        404 - the queried role does not exist
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(
                self.account,
                'user',
                'fakeUser',
                all=''
            )

        self.assertEqual(context.exception.status, 404)

    # Test cases for getting a role's direct memberships

    def test_get_direct_memberships_200(self):
        """Test case for 200 status response for GET requests using 'memberships' query parameter
        Queries user:bob for all its memberships, expanded recursively
        This will include memberships of bob's direct memberships
        """
        # Set bob as member of userGroup and anotherGroup
        # Set userGroup as member of testLayer
        self.add_user_to_group('bob')

        self.api.add_member(
            self.account,
            'group',
            'anotherGroup',
            members='',
            member=self.BOB_ID
        )

        self.api.add_member(
            self.account,
            'layer',
            'testLayer',
            members='',
            member=self.GROUP_ID
        )

        # testLayer will not be listed in direct memberships of bob
        bob_membership_data, status, _ = self.api.get_role_with_http_info(
            self.account,
            'user',
            'bob',
            memberships=''
        )

        target_membership_data = [
            {
                'admin_option': False,
                'ownership': False,
                'role': f'{self.account}:group:userGroup',
                'member': f'{self.account}:user:bob'
            },
            {
                'admin_option': False,
                'ownership': False,
                'role': f'{self.account}:group:anotherGroup',
                'member': f'{self.account}:user:bob'
            }
        ]

        self.assertEqual(status, 200)
        self.assertEqual(bob_membership_data, target_membership_data)

    def test_get_direct_memberships_400(self):
        """Test case for 400 status response for GET requests using 'memberships' query parameter
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(
                self.account,
                NULL_BYTE,
                'admin',
                memberships=''
            )

        self.assertEqual(context.exception.status, 400)

    def test_get_direct_memberships_401(self):
        """Test case for 401 status response for GET requests using 'memberships' query parameter
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.get_role(
                self.account,
                'user',
                'admin',
                memberships=''
            )

        self.assertEqual(context.exception.status, 401)

    def test_get_direct_memberships_404(self):
        """Test case for 404 status response for GET requests using 'memberships' query parameter
        404 - the queried role does not exist
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(
                self.account,
                'user',
                'fakeUser',
                memberships=''
            )

        self.assertEqual(context.exception.status, 404)

    def test_get_direct_memberships_422(self):
        """Test case for 422 status response for GET requests using 'memberships' query parameter
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(
                self.account,
                'user',
                'admin',
                memberships='',
                search=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

    # Test cases for getting a role's members

    def test_get_members_200(self):
        """Test case for 200 status response for GET requests using 'members' query parameter
        Queries group:userGroup role for its members, which should only be dev:user:admin
        """
        group_member_data, status, _ = self.api.get_role_with_http_info(
            self.account,
            'group',
            'userGroup',
            members=''
        )

        target_response = [
            {
                'admin_option': True,
                'ownership': True,
                'role': self.GROUP_ID,
                'member': self.ADMIN_ID,
                'policy': self.ROOT_ID
            }
        ]

        self.assertEqual(status, 200)
        self.assertEqual(group_member_data, target_response)

    def test_get_members_400(self):
        """Test case for 400 status response for GET requests using 'members' query parameter
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(
                self.account,
                NULL_BYTE,
                'admin',
                members=''
            )

        self.assertEqual(context.exception.status, 400)

    def test_get_members_401(self):
        """Test case for 401 status response for GET requests using 'members' query parameter
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.get_role(
                self.account,
                'user',
                'admin',
                members=''
            )

        self.assertEqual(context.exception.status, 401)

    def test_get_members_404(self):
        """Test case for 404 status response for GET requests using 'members' query parameter
        404 - the queried role does not exist
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(
                self.account,
                'user',
                'fakeUser',
                members=''
            )

        self.assertEqual(context.exception.status, 404)

    def test_get_members_422(self):
        """Test case for 422 status response for GET requests using 'members' query parameter
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.get_role(
                self.account,
                'user',
                'admin',
                members='',
                search=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

    # Test cases confirming count, offset, limit and search query parameters

    def test_get_members_count(self):
        """Test using members & count query parameters on GET
        Adds dev:user:bob as a member of group:userGroup, then queries for a member count
        """
        self.add_user_to_group('bob')
        self.add_user_to_group('alice')

        response = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members='',
            count=True
        )

        self.assertEqual(response['count'], 3)

    def test_get_members_offset(self):
        """Test using members & offset query parameters on GET requests
        Returns member data starting at <offset>
        """
        self.add_user_to_group('bob')
        self.add_user_to_group('alice')

        response = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members='',
            offset=2
        )

        # starting at offset 2 should omit user:admin (0) and user:alice (1)
        target_response = [
            {
                'admin_option': False,
                'ownership': False,
                'role': self.GROUP_ID,
                'member': self.BOB_ID
            }
        ]

        self.assertEqual(response, target_response)

    def test_get_members_limit(self):
        """Test using members & limit query parameters on GET requests
        Returns member data limited to the first <limit> results
        """
        self.add_user_to_group('bob')
        self.add_user_to_group('alice')

        response = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members='',
            limit=2
        )

        # limiting the results to the first 2 should omit user:bob (idx 2)
        target_response = [
            {
                'admin_option': True,
                'ownership': True,
                'role': self.GROUP_ID,
                'member': self.ADMIN_ID,
                'policy': self.ROOT_ID
            },
            {
                'admin_option': False,
                'ownership': False,
                'role': self.GROUP_ID,
                'member': self.ALICE_ID
            }
        ]

        self.assertEqual(response, target_response)

    def test_get_members_search(self):
        """Test using members & search query parameters on GET requests
        Returns only members matching the provided string
        """
        self.add_user_to_group('bob')
        self.add_user_to_group('alice')

        response = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members='',
            search='bob'
        )

        target_response = [
            {
                'admin_option': False,
                'ownership': False,
                'role': self.GROUP_ID,
                'member': self.BOB_ID
            }
        ]

        self.assertEqual(response, target_response)

    # Test cases for POST requests to /roles/{account}/{kind}/{identifier}?members&member="{role}"

    def test_add_member_204(self):
        """Test case for 204 status response when adding role member
        This endpoint will assign a given role as a member to another role
        The example shown here is a user Bob being assigned as a member of a group
        204 - successful member assignment, empty response body
        """
        _, status, _ = self.add_user_to_group('bob')
        self.assertEqual(status, 204)

        group_member_data = self.api.get_role(
            self.account,
            'group',
            'userGroup',
            members=''
        )

        self.assertEqual(len(group_member_data), 2)
        members = [self.ADMIN_ID, self.BOB_ID]
        for i in range(0, 2):
            self.assertEqual(group_member_data[i]['member'], members[i])

    def test_add_member_400(self):
        """Test case for 400 status response when adding role member
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.add_member(
                self.account,
                NULL_BYTE,
                'userGroup',
                members='',
                member=self.BOB_ID
            )

        self.assertEqual(context.exception.status, 400)

    def test_add_member_401(self):
        """Test case for 401 status response when adding role member
        401 - unauthorized request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.add_member(
                self.account,
                'group',
                'userGroup',
                members='',
                member=self.BOB_ID
            )

        self.assertEqual(context.exception.status, 401)

    def test_add_member_403(self):
        """Test case for 403 status response when adding role member
        403 - the authenticated user lacks the necessary privilege
        """
        # establish a new api client as user Bob
        bob_client = api_config.get_api_client(username='bob')
        bob_roles_api = openapi_client.RolesApi(bob_client)

        # attempt to add Alice as a member of userGroup as Bob
        with self.assertRaises(openapi_client.ApiException) as context:
            bob_roles_api.add_member(
                self.account,
                'group',
                'userGroup',
                members='',
                member=self.ALICE_ID
            )

        self.assertEqual(context.exception.status, 403)

    def test_add_member_404(self):
        """Test case for 404 status response when adding role member
        404 - the role inteded for assignment as member does not exist
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.add_member(
                self.account,
                'group',
                'userGroup',
                members='',
                member=f'{self.account}:user:fakeUser'
            )

        self.assertEqual(context.exception.status, 404)

    def test_add_member_422(self):
        """Test case for 422 status response when adding role member
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.add_member(
                self.account,
                'group',
                'userGroup',
                members='',
                member=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

    # Test cases for DELETE requests to /roles/{account}/{kind}/{identifier}?members&member="{role}"

    def test_delete_member_204(self):
        """Test case for 204 status response when deleting role member
        204 - successful request, the specified member is no longer a member of the role
        """
        # add Bob as a member of userGroup and confirm
        self.add_user_to_group('bob')
        group_members = self.api.get_role(self.account, 'group', 'userGroup', members='')
        self.assertEqual(len(group_members), 2)
        self.assertEqual(group_members[1]['member'], self.BOB_ID)

        # remove Bob as member of userGroup
        _, delete_status, _ = self.api.delete_member_with_http_info(
            self.account,
            'group',
            'userGroup',
            members='',
            member=self.BOB_ID
        )
        self.assertEqual(delete_status, 204)

        # confirm Bob's removal as member
        group_members = self.api.get_role(self.account, 'group', 'userGroup', members='')
        self.assertEqual(len(group_members), 1)
        self.assertNotEqual(group_members[0]['member'], self.BOB_ID)

    def test_delete_member_400(self):
        """Test case for 400 status response when deleting role member
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.delete_member(
                self.account,
                NULL_BYTE,
                'userGroup',
                members='',
                member=self.BOB_ID
            )

        self.assertEqual(context.exception.status, 400)

    def test_delete_member_401(self):
        """Test case for 401 status response when deleting role member
        401 - unauthenticated request
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.bad_auth_api.delete_member(
                self.account,
                'group',
                'userGroup',
                members='',
                member=self.BOB_ID
            )

        self.assertEqual(context.exception.status, 401)

    def test_delete_member_403(self):
        """Test case for 403 status response when deleting role member
        403 - the authenticated client lacks the necessary privilege
        """
        # add Alice as a member of userGroup and confirm
        self.add_user_to_group('alice')
        group_members = self.api.get_role(self.account, 'group', 'userGroup', members='')
        self.assertEqual(len(group_members), 2)
        self.assertEqual(group_members[1]['member'], self.ALICE_ID)

        # establish a new api client as user Bob
        bob_client = api_config.get_api_client(username='bob')
        bob_roles_api = openapi_client.RolesApi(bob_client)

        # attempt to delete Alice as member of userGroup as Bob
        with self.assertRaises(openapi_client.ApiException) as context:
            bob_roles_api.delete_member(
                self.account,
                'group',
                'userGroup',
                members='',
                member=self.ALICE_ID
            )

        self.assertEqual(context.exception.status, 403)

    def test_delete_member_404(self):
        """Test case for 404 status response when deleting role member
        404 - the queried role intended for deletion was not found
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.delete_member(
                self.account,
                'group',
                'userGroup',
                members='',
                member=f'{self.account}:user:fakeUser'
            )

        self.assertEqual(context.exception.status, 404)

    def test_delete_member_422(self):
        """Test case for 422 status response when deleting role member
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(openapi_client.ApiException) as context:
            self.api.delete_member(
                self.account,
                'group',
                'userGroup',
                members='',
                member=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
