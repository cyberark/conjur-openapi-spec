from __future__ import absolute_import

import unittest

import conjur

from . import api_config


class TestPublicKeysApi(api_config.ConfiguredTest):
    """PublicKeysApi unit test stubs"""

    def setUp(self):
        self.api = conjur.api.public_keys_api.PublicKeysApi(self.client)

    def test_show(self):
        """Test case for show

        Shows all public keys for a resource.
        """
        resp = self.api.show_public_keys(self.account, 'Variable', 'one/password')

        self.assertIsInstance(resp, str)


if __name__ == '__main__':
    unittest.main()
