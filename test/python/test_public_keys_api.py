from __future__ import absolute_import

import unittest

import openapi_client
import openapi_client.apis

from . import api_config


class TestPublicKeysApi(api_config.ConfiguredTest):
    """PublicKeysApi unit test stubs"""

    def setUp(self):
        self.api = openapi_client.apis.PublicKeysApi(self.client)

    def test_show_public_keys(self):
        """Test case for show_public_keys

        Shows all public keys for a resource.
        """
        resp = self.api.show_public_keys(self.account, 'Variable', 'one/password')

        self.assertIsInstance(resp, str)


if __name__ == '__main__':
    unittest.main()
