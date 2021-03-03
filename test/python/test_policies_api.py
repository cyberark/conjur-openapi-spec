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

    def test_replace_policy_201(self):
        """Test case for replace_policy 201 response

        Loads or replace_policys a Conjur policy document.
        """
        _, status, _ = self.api.replace_policy_with_http_info(self.account, 'root', TEST_POLICY)

        self.assertEqual(status, 201)

    def test_replace_policy_401(self):
        """Test case for replace_policy 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.replace_policy(self.account, 'root', TEST_POLICY)

        self.assertEqual(context.exception.status, 401)

    def test_replace_policy_400(self):
        """Test case for replace_policy 400 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.replace_policy(self.account, '\00', TEST_POLICY)

        self.assertEqual(context.exception.status, 400)

    def test_replace_policy_403(self):
        """Test case for replace_policy 403 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.alice_api.replace_policy(self.account, 'root', TEST_POLICY)

        self.assertEqual(context.exception.status, 403)

    def test_replace_policy_404(self):
        """Test case for replace_policy 404 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.replace_policy(self.account, 'nonexist', TEST_POLICY)

        self.assertEqual(context.exception.status, 404)

    def test_replace_policy_422(self):
        """Test case for replace_policy 422 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.replace_policy(self.account, 'root', '\00')

        self.assertEqual(context.exception.status, 422)

    def test_update_policy_201(self):
        """Test case for update_policy 201 response

        Modifies an existing Conjur policy.
        """
        _, status, _ = self.api.update_policy_with_http_info(self.account, 'root', MODIFY_POLICY)

        self.assertEqual(status, 201)

    def test_update_policy_400(self):
        """Test case for update_policy 400 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.update_policy(self.account, '\00', MODIFY_POLICY)

        self.assertEqual(context.exception.status, 400)

    def test_update_policy_401(self):
        """Test case for update_policy 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.update_policy(self.account, 'root', MODIFY_POLICY)

        self.assertEqual(context.exception.status, 401)

    def test_update_policy_403(self):
        """Test case for update_policy 403 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.alice_api.update_policy(self.account, 'root', MODIFY_POLICY)

        self.assertEqual(context.exception.status, 403)

    def test_update_policy_404(self):
        """Test case for update_policy 404 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.update_policy(self.account, 'nonexist', MODIFY_POLICY)

        self.assertEqual(context.exception.status, 404)

    def test_update_policy_422(self):
        """Test case for update_policy 422 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.update_policy(self.account, 'root', '\00')

        self.assertEqual(context.exception.status, 422)

    def test_load_policy_201(self):
        """Test case for load_policy 201 response

        Adds data to the existing Conjur policy.
        """
        _, status, _ = self.api.load_policy_with_http_info(self.account, 'root', UPDATE_POLICY)

        self.assertEqual(status, 201)

    def test_load_policy_400(self):
        """Test case for load_policy 400 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.load_policy(self.account, '\00', UPDATE_POLICY)

        self.assertEqual(context.exception.status, 400)

    def test_load_policy_401(self):
        """Test case for load_policy 401 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.bad_auth_api.load_policy(self.account, 'root', UPDATE_POLICY)

        self.assertEqual(context.exception.status, 401)

    def test_load_policy_403(self):
        """Test case for load_policy 403 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.alice_api.load_policy(self.account, 'root', UPDATE_POLICY)

        self.assertEqual(context.exception.status, 403)

    def test_load_policy_404(self):
        """Test case for load_policy 404 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.load_policy(self.account, 'nonexist', UPDATE_POLICY)

        self.assertEqual(context.exception.status, 404)

    def test_load_policy_422(self):
        """Test case for load_policy 422 response"""
        with self.assertRaises(conjur.exceptions.ApiException) as context:
            self.api.load_policy(self.account, 'root', '\00')

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
