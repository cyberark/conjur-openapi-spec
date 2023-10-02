from __future__ import absolute_import

import unittest

from conjur import ApiException

from . import test_roles_api
from .test_roles_api import NULL_BYTE

class TestRolesMembersApi(test_roles_api.TestRolesApi):
    """Test RolesApi calls for getting a role's members and memberships"""

    # Test cases for getting a role's members

    def test_get_members_200(self):
        """Test case for 200 status response for GET requests using 'members' query parameter
        Queries group:userGroup role for its members, which should only be dev:user:admin
        """
        response = self.api.show_role_with_http_info(
            self.account,
            'group',
            'userGroup',
            members=''
        )

        target_response = [
            {
                'admin_option': True,
                'ownership': True,
                'role': self.USER_GROUP_ID,
                'member': self.ADMIN_ID,
                'policy': self.ROOT_ID
            }
        ]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, target_response)

    def test_get_members_400(self):
        """Test case for 400 status response for GET requests using 'members' query parameter
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_role(
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
        with self.assertRaises(ApiException) as context:
            self.bad_auth_api.show_role(
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
        with self.assertRaises(ApiException) as context:
            self.api.show_role(
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
        with self.assertRaises(ApiException) as context:
            self.api.show_role(
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

        self.api.add_member_to_role(
            self.account,
            'group',
            'anotherGroup',
            members='',
            member=self.BOB_ID
        )

        self.api.add_member_to_role(
            self.account,
            'layer',
            'testLayer',
            members='',
            member=self.USER_GROUP_ID
        )

        # testLayer will be listed in all memberships of bob
        response = self.api.show_role_with_http_info(
            self.account,
            'user',
            'bob',
            all=''
        )

        target_membership_data = [
            self.LAYER_ID,
            self.ANOTHER_GROUP_ID,
            self.USER_GROUP_ID,
            self.BOB_ID
        ]

        self.assertEqual(response.status_code, 200)
        for i in response.data:
            self.assertIn(i, target_membership_data)

    def test_get_all_memberships_400(self):
        """Test case for 400 status response for GET requests using 'all' query parameter
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_role(
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
        with self.assertRaises(ApiException) as context:
            self.bad_auth_api.show_role(
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
        with self.assertRaises(ApiException) as context:
            self.api.show_role(
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

        self.api.add_member_to_role(
            self.account,
            'group',
            'anotherGroup',
            members='',
            member=self.BOB_ID
        )

        self.api.add_member_to_role(
            self.account,
            'layer',
            'testLayer',
            members='',
            member=self.USER_GROUP_ID
        )

        # testLayer will not be listed in direct memberships of bob
        response = self.api.show_role_with_http_info(
            self.account,
            'user',
            'bob',
            memberships=''
        )

        memberships = [f'{self.account}:group:userGroup', f'{self.account}:group:anotherGroup']

        self.assertEqual(response.status_code, 200)
        for i in range(0, 2):
            self.assertIn(response.data[i]['role'], memberships)

    def test_get_direct_memberships_400(self):
        """Test case for 400 status response for GET requests using 'memberships' query parameter
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(ApiException) as context:
            self.api.show_role(
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
        with self.assertRaises(ApiException) as context:
            self.bad_auth_api.show_role(
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
        with self.assertRaises(ApiException) as context:
            self.api.show_role(
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
        with self.assertRaises(ApiException) as context:
            self.api.show_role(
                self.account,
                'user',
                'admin',
                memberships='',
                search=NULL_BYTE
            )

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
