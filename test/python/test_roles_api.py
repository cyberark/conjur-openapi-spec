from __future__ import absolute_import

import unittest
import os

import openapi_client

from . import api_config
from .api_config import CONJUR_ACCOUNT

class TestRolesApi(unittest.TestCase):
    """RolesApi unit test stubs"""
    @classmethod
    def setUpClass(cls):
        cls.account = os.environ[CONJUR_ACCOUNT]

        cls.client = api_config.get_api_client()

    def setUp(self):
        self.api = openapi_client.api.roles_api.RolesApi(self.client)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

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
