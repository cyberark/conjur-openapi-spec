from __future__ import absolute_import

import unittest

import openapi_client

from . import api_config

class TestRolesApi(api_config.ConfiguredTest):
    """RolesApi unit test stubs"""
    def setUp(self):
        self.api = openapi_client.api.roles_api.RolesApi(self.client)

    def test_get_role(self):
        """Test case for get_role

        Get role information
        """
        details = self.api.get_role(self.account, 'user', 'admin')

        self.assertIsInstance(details, dict)
        members = ['created_at', 'id', 'members']
        for i in members:
            self.assertIn(i, details)

if __name__ == '__main__':
    unittest.main()
