from __future__ import absolute_import

import unittest

import conjur

from .. import api_config

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
        cls.BOB_ID = f'{cls.account}:user:bob'
        cls.USER_GROUP_ID = f'{cls.account}:group:userGroup'
        cls.ANOTHER_GROUP_ID = f'{cls.account}:group:anotherGroup'
        cls.LAYER_ID = f'{cls.account}:layer:testLayer'
        cls.ROOT_ID = f'{cls.account}:policy:root'

    def setUp(self):
        self.api = conjur.RolesApi(self.client)
        self.bad_auth_api = conjur.RolesApi(self.bad_auth_client)

        # set a new root policy including a new group and users Alice and Bob
        # these will be used to test member addition/deletion
        policy_api = conjur.PoliciesApi(self.client)
        policy_api.replace_policy(self.account, 'root', ROLES_POLICY)

    def tearDown(self):
        super().load_default_policy()

    def add_user_to_group(self, identifier):
        """Adds a given user to the group defined in ROLES_POLICY
        """
        role_id = f'{self.account}:user:{identifier}'
        response = self.api.add_member_to_role_with_http_info(
            self.account,
            'group',
            'userGroup',
            members='',
            member=role_id
        )
        return response

    # Test cases for GET requests to /roles/{account}/{kind}/{identifier} endpoint

    def test_show_role_200(self):
        """Test case for 200 status response when getting role data
        Gets information on the specified role
        """
        role_details, status, _ = self.api.show_role_with_http_info(self.account, 'user', 'admin')

        self.assertEqual(status, 200)
        self.assertIsInstance(role_details, dict)

        members = ['created_at', 'id', 'members']
        for i in members:
            self.assertIn(i, role_details)

    def test_show_role_400(self):
        """Test case for 400 status response when getting role data
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.show_role(self.account, NULL_BYTE, 'admin')

        self.assertEqual(context.exception.status, 400)

    def test_show_role_401(self):
        """Test case for 401 status response when getting role data
        401 - unauthorized request
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.show_role(self.account, 'user', 'admin')

        self.assertEqual(context.exception.status, 401)

    def test_show_role_404(self):
        """Test case for 404 status response when getting role data
        404 - the role could not be found
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.show_role(self.account, 'user', 'fakeUser')

        self.assertEqual(context.exception.status, 404)

    def test_show_role_422(self):
        """Test case for 422 status response when getting role data
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.show_role(
                self.account,
                'user',
                'admin',
                members='',
                search=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

    # Test cases for POST requests to /roles/{account}/{kind}/{identifier}?members&member="{role}"

    def test_add_member_to_role_204(self):
        """Test case for 204 status response when adding role member
        This endpoint will assign a given role as a member to another role
        The example shown here is a user Bob being assigned as a member of a group
        204 - successful member assignment, empty response body
        """
        _, status, _ = self.add_user_to_group('bob')
        self.assertEqual(status, 204)

        group_member_data = self.api.show_role(
            self.account,
            'group',
            'userGroup',
            members=''
        )

        self.assertEqual(len(group_member_data), 2)
        members = [self.ADMIN_ID, self.BOB_ID]
        for i in range(0, 2):
            self.assertEqual(group_member_data[i]['member'], members[i])

    def test_add_member_to_role_400(self):
        """Test case for 400 status response when adding role member
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.add_member_to_role(
                self.account,
                NULL_BYTE,
                'userGroup',
                members='',
                member=self.BOB_ID
            )

        self.assertEqual(context.exception.status, 400)

    def test_add_member_to_role_401(self):
        """Test case for 401 status response when adding role member
        401 - unauthorized request
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.add_member_to_role(
                self.account,
                'group',
                'userGroup',
                members='',
                member=self.BOB_ID
            )

        self.assertEqual(context.exception.status, 401)

    def test_add_member_to_role_404(self):
        """Test case for 404 status response when adding role member
        404 - the role inteded for assignment as member does not exist
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.add_member_to_role(
                self.account,
                'group',
                'userGroup',
                members='',
                member=f'{self.account}:user:fakeUser'
            )

        self.assertEqual(context.exception.status, 404)

    def test_add_member_to_role_422(self):
        """Test case for 422 status response when adding role member
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.add_member_to_role(
                self.account,
                'group',
                'userGroup',
                members='',
                member=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

    # Test cases for DELETE requests to /roles/{account}/{kind}/{identifier}?members&member="{role}"

    def test_remove_member_from_role_204(self):
        """Test case for 204 status response when deleting role member
        204 - successful request, the specified member is no longer a member of the role
        """
        # add Bob as a member of userGroup and confirm
        self.add_user_to_group('bob')
        group_members = self.api.show_role(self.account, 'group', 'userGroup', members='')
        self.assertEqual(len(group_members), 2)
        self.assertEqual(group_members[1]['member'], self.BOB_ID)

        # remove Bob as member of userGroup
        _, delete_status, _ = self.api.remove_member_from_role_with_http_info(
            self.account,
            'group',
            'userGroup',
            members='',
            member=self.BOB_ID
        )
        self.assertEqual(delete_status, 204)

        # confirm Bob's removal as member
        group_members = self.api.show_role(self.account, 'group', 'userGroup', members='')
        self.assertEqual(len(group_members), 1)
        self.assertNotEqual(group_members[0]['member'], self.BOB_ID)

    def test_remove_member_from_role_400(self):
        """Test case for 400 status response when deleting role member
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.remove_member_from_role(
                self.account,
                NULL_BYTE,
                'userGroup',
                members='',
                member=self.BOB_ID
            )

        self.assertEqual(context.exception.status, 400)

    def test_remove_member_from_role_401(self):
        """Test case for 401 status response when deleting role member
        401 - unauthenticated request
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.remove_member_from_role(
                self.account,
                'group',
                'userGroup',
                members='',
                member=self.BOB_ID
            )

        self.assertEqual(context.exception.status, 401)

    def test_remove_member_from_role_404(self):
        """Test case for 404 status response when deleting role member
        404 - the queried role intended for deletion was not found
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.remove_member_from_role(
                self.account,
                'group',
                'userGroup',
                members='',
                member=f'{self.account}:user:fakeUser'
            )

        self.assertEqual(context.exception.status, 404)

    def test_remove_member_from_role_422(self):
        """Test case for 422 status response when deleting role member
        422 - Conjur recieved a malformed request parameter
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.remove_member_from_role(
                self.account,
                'group',
                'userGroup',
                members='',
                member=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
