from __future__ import absolute_import

import unittest

import openapi_client

from . import api_config

WHOAMI_FIELDS = [
    "client_ip",
    "user_agent",
    "account",
    "username",
    "token_issued_at",
]

class TestWhoamiApi(api_config.ConfiguredTest):
    """WhoamiApi unit test stubs"""

    def setUp(self):
        self.api = openapi_client.api.status_api.StatusApi(self.client)
        self.bad_auth_api = openapi_client.api.status_api.StatusApi(self.bad_auth_client)

    def test_who_am_i_200(self):
        """Test case for who_am_i 200 response"""
        result = self.api.who_am_i()

        self.assertIsInstance(result, openapi_client.models.who_am_i.WhoAmI)

        for i in WHOAMI_FIELDS:
            value = getattr(result, i)
            # Just make sure that all the attributes have a value assigned to them
            self.assertNotEqual(value, '')

    def test_who_am_i_401(self):
        """Test case for who_am_i 401 response"""
        with self.assertRaises(openapi_client.exceptions.ApiException) as context:
            self.bad_auth_api.who_am_i()

        self.assertEqual(context.exception.status, 401)

if __name__ == '__main__':
    unittest.main()
