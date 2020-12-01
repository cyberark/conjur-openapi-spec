from __future__ import absolute_import

import unittest
import os

import openapi_client

from . import api_config
from .api_config import CONJUR_ACCOUNT

RESOURCE_MEMBERS = ['created_at', 'id', 'owner']

class TestResourcesApi(unittest.TestCase):
    """ResourcesApi unit test stubs"""

    @classmethod
    def setUpClass(cls):
        cls.account = os.environ[CONJUR_ACCOUNT]

        cls.client = api_config.get_api_client()

    def setUp(self):
        self.api = openapi_client.api.resources_api.ResourcesApi(self.client)

    def test_get_resource(self):
        """Test case for get_resource

        Shows a description of a single resource.
        """
        resource_info = self.api.get_resource(self.account, 'variable', 'testSecret')

        self.assertIsInstance(resource_info, dict)

        for i in RESOURCE_MEMBERS:
            self.assertIn(i, resource_info)

    def test_get_resources(self):
        """Test case for get_resources

        Lists resources within an organization account.
        """
        resources = self.api.get_resources(self.account)

        self.assertIsInstance(resources, list)
        for resource in resources:
            for member in RESOURCE_MEMBERS:
                self.assertIn(member, resource)


if __name__ == '__main__':
    unittest.main()
