from __future__ import absolute_import

import unittest

import conjur

from . import test_roles_api
from .test_roles_api import NULL_BYTE
from .. import api_config

class TestRolesQueryParamsApi(test_roles_api.TestRolesApi):
    """Test RolesApi function calls with query parameters"""

    # Test cases confirming count, offset, limit and search query parameters

    def test_get_members_count(self):
        """Test using members & count query parameters on GET
        Adds dev:user:bob as a member of group:userGroup, then queries for a member count
        """
        self.add_user_to_group('bob')
        self.add_user_to_group('alice')

        response = self.api.show_role(
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

        response = self.api.show_role(
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
                'role': self.USER_GROUP_ID,
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

        response = self.api.show_role(
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
                'role': self.USER_GROUP_ID,
                'member': self.ADMIN_ID,
                'policy': self.ROOT_ID
            },
            {
                'admin_option': False,
                'ownership': False,
                'role': self.USER_GROUP_ID,
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

        response = self.api.show_role(
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
                'role': self.USER_GROUP_ID,
                'member': self.BOB_ID
            }
        ]

        self.assertEqual(response, target_response)

    # Test cases for getting a role membership graph

    def test_show_graph_200(self):
        """Test case for show 200 response with graph query param"""
        details, status, _ = self.api.show_role_with_http_info(
            self.account,
            'user',
            'admin',
            graph=''
        )

        self.assertEqual(status, 200)
        # root policy as parent should always be first for admin user
        for i in details:
            self.assertIn('parent', i)
            self.assertIn('child', i)

    def test_show_graph_400(self):
        """Test case for show_role 400 response with graph query param"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.show_role(self.account, 'user', NULL_BYTE, graph='')

        self.assertEqual(context.exception.status, 400)

    def test_show_graph_401(self):
        """Test case for show_role 401 response with graph query param"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.show_role(self.account, 'user', 'admin', graph='')

        self.assertEqual(context.exception.status, 401)

    def test_show_graph_404(self):
        """Test case for show_role 404 response with graph query param"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.show_role(self.account, 'user', 'nonexist', graph='')

        self.assertEqual(context.exception.status, 404)

    # Test combinations of optional query parameters when getting role information

    def test_parameter_combos_a(self):
        """Test Conjur's response to being given all optional parameters in a single request
        Conjur responds with `graph` results ONLY
        """
        details, status, _ = self.api.show_role_with_http_info(
            self.account,
            'user',
            'admin',
            all='',
            memberships='',
            members='',
            graph=''
        )

        self.assertEqual(status, 200)

        for i in details:
            self.assertIn('parent', i)
            self.assertIn('child', i)

    def test_parameter_combos_b(self):
        """Test Conjur's response to being given all optional parameters besides `graph`
        Conjur responses with `all` results ONLY
        """
        details, status, _ = self.api.show_role_with_http_info(
            self.account,
            'user',
            'admin',
            all='',
            memberships='',
            members=''
        )

        target_details = [
            self.ROOT_ID,
            self.LAYER_ID,
            self.ANOTHER_GROUP_ID,
            self.ALICE_ID,
            self.USER_GROUP_ID,
            self.ADMIN_ID,
            self.BOB_ID
        ]

        if api_config.ENTERPRISE_TESTS:
            target_details.append('!:!:root')

        self.assertEqual(status, 200)
        for i in target_details:
            # This will throw an error causing the test to fail if
            # i is not present in details
            details.remove(i)

        self.assertEqual(len(details), 0)

    def test_parameter_combos_c(self):
        """Test Conjur's response to being given both `members` and `memberships`
        Conjur response with `memberships` results ONLY
        """
        self.add_user_to_group('bob')

        details, status, _ = self.api.show_role_with_http_info(
            self.account,
            'user',
            'bob',
            memberships='',
            members=''
        )

        target_details = {
                'admin_option': False,
                'ownership': False,
                'role': self.USER_GROUP_ID,
                'member': self.BOB_ID
            }

        self.assertEqual(status, 200)
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0], target_details)

if __name__ == '__main__':
    unittest.main()
