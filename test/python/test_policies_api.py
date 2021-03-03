from __future__ import absolute_import

import unittest

import conjur

from . import api_config

NEW_VARIABLE = 'policy/test'

TEST_POLICY = f'''
- !variable one/password
- !variable testSecret
- !variable {NEW_VARIABLE}
'''

MODIFY_POLICY = f'''
- !delete
  record: !variable {NEW_VARIABLE}
'''

UPDATE_POLICY = f'''
- !variable {NEW_VARIABLE}
'''

class TestPoliciesApi(api_config.ConfiguredTest):
    """PoliciesApi unit test stubs"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        alice_client = api_config.get_api_client(username='alice')
        cls.alice_api = conjur.api.policies_api.PoliciesApi(alice_client)

    def setUp(self):
        self.api = conjur.api.policies_api.PoliciesApi(self.client)
        self.bad_auth_api = conjur.api.policies_api.PoliciesApi(self.bad_auth_client)

    def test_replace_201(self):
        """Test case for replace 201 response

        Loads or replaces a Conjur policy document.
        """
        _, status, _ = self.api.replace_with_http_info(self.account, 'root', TEST_POLICY)

        self.assertEqual(status, 201)

    def test_replace_401(self):
        """Test case for replace 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.replace(self.account, 'root', TEST_POLICY)

        self.assertEqual(context.exception.status, 401)

    def test_replace_400(self):
        """Test case for replace 400 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.replace(self.account, '\00', TEST_POLICY)

        self.assertEqual(context.exception.status, 400)

    def test_replace_403(self):
        """Test case for replace 403 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.alice_api.replace(self.account, 'root', TEST_POLICY)

        self.assertEqual(context.exception.status, 403)

    def test_replace_404(self):
        """Test case for replace 404 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.replace(self.account, 'nonexist', TEST_POLICY)

        self.assertEqual(context.exception.status, 404)

    def test_replace_422(self):
        """Test case for replace 422 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.replace(self.account, 'root', '\00')

        self.assertEqual(context.exception.status, 422)

    def test_update_201(self):
        """Test case for update 201 response

        Modifies an existing Conjur policy.
        """
        _, status, _ = self.api.update_with_http_info(self.account, 'root', MODIFY_POLICY)

        self.assertEqual(status, 201)

    def test_update_400(self):
        """Test case for update 400 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.update(self.account, '\00', MODIFY_POLICY)

        self.assertEqual(context.exception.status, 400)

    def test_update_401(self):
        """Test case for update 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.update(self.account, 'root', MODIFY_POLICY)

        self.assertEqual(context.exception.status, 401)

    def test_update_403(self):
        """Test case for update 403 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.alice_api.update(self.account, 'root', MODIFY_POLICY)

        self.assertEqual(context.exception.status, 403)

    def test_update_404(self):
        """Test case for update 404 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.update(self.account, 'nonexist', MODIFY_POLICY)

        self.assertEqual(context.exception.status, 404)

    def test_update_422(self):
        """Test case for update 422 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.update(self.account, 'root', '\00')

        self.assertEqual(context.exception.status, 422)

    def test_append_201(self):
        """Test case for append 201 response

        Adds data to the existing Conjur policy.
        """
        _, status, _ = self.api.append_with_http_info(self.account, 'root', UPDATE_POLICY)

        self.assertEqual(status, 201)

    def test_append_400(self):
        """Test case for append 400 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.append(self.account, '\00', UPDATE_POLICY)

        self.assertEqual(context.exception.status, 400)

    def test_append_401(self):
        """Test case for append 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.append(self.account, 'root', UPDATE_POLICY)

        self.assertEqual(context.exception.status, 401)

    def test_append_403(self):
        """Test case for append 403 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.alice_api.append(self.account, 'root', UPDATE_POLICY)

        self.assertEqual(context.exception.status, 403)

    def test_append_404(self):
        """Test case for append 404 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.append(self.account, 'nonexist', UPDATE_POLICY)

        self.assertEqual(context.exception.status, 404)

    def test_append_422(self):
        """Test case for append 422 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.append(self.account, 'root', '\00')

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
