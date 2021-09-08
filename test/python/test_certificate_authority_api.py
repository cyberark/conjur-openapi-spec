from __future__ import absolute_import

import pathlib
import unittest

import conjur

from . import api_config

CA_POLICY = pathlib.Path('test/config/cert_auth_policy.yml')
CERT_CHAIN_PATH = pathlib.Path('config/https/ca.crt')
UNENCRYPTED_KEY_PATH = pathlib.Path('config/https/intermediate.key')
ENCRYPTED_KEY_PATH = pathlib.Path('config/https/intermediate_encrypted.key')
KEY_PASSWORD_PATH = pathlib.Path('config/https/intermediate_key_password.txt')
CSR_PATH = pathlib.Path('test-python.csr')

def read_file(path):
    """Returns the entirety of a file's contents"""
    with open(path, 'r', encoding="utf-8") as content:
        return content.read()

class TestCertificateAuthorityApi(api_config.ConfiguredTest):
    """CertificateAuthorityApi unit test stubs"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.CA_SERVICE_ID = 'signing-service'

        cls.TEST_CLIENT_ID    = f'{cls.account}:host:{cls.CA_SERVICE_ID}/test-client'
        cls.CN_TEST_CLIENT_ID = f'{cls.account}:host:{cls.CA_SERVICE_ID}/cn-test-client'
        cls.NO_SIGN_CLIENT_ID = f'{cls.account}:host:{cls.CA_SERVICE_ID}/no-sign-client'

        # read generated CSR
        cls.csr = read_file(CSR_PATH)

    def setUp(self):
        # load CA policy as root
        # creates a CA webservice,
        # a group with sign privilege on the service,
        # and host clients with varying privilege
        ca_policy = read_file(CA_POLICY)
        policy_api = conjur.PoliciesApi(self.client)
        policy_api.replace_policy(
            self.account,
            'root',
            ca_policy
        )

        # set up Certificate Authority API clients
        client = api_config.get_api_client(
            'signing-service/test-client',
            'host'
        )
        self.api = conjur.CertificateAuthorityApi(client)
        self.bad_auth_api = conjur.CertificateAuthorityApi(self.bad_auth_client)

        # assign intermediate CA private key and CA chain to Conjur variables
        ca_chain = read_file(CERT_CHAIN_PATH)
        private_key = read_file(UNENCRYPTED_KEY_PATH)

        self.secrets_api = conjur.SecretsApi(self.client)
        self.update_ca_chain(ca_chain)
        self.update_ca_private_key(private_key)

    def update_ca_chain(self, ca_chain):
        """Configure a Conjur CA with a new certificate chain"""
        self.secrets_api.create_secret(
            self.account,
            'variable',
            f'conjur/{self.CA_SERVICE_ID}/ca/cert-chain',
            body=ca_chain
        )

    def update_ca_private_key(self, private_key):
        """Configures a Conjur CA with a new private key
        Encrypted private keys must be PKCS#8 encoded
        """
        self.secrets_api.create_secret(
            self.account,
            'variable',
            f'conjur/{self.CA_SERVICE_ID}/ca/private-key',
            body=private_key
        )

    def update_ca_key_password(self, key_password):
        """Configures a Conjur CA with a new private key password"""
        self.secrets_api.create_secret(
            self.account,
            'variable',
            f'conjur/{self.CA_SERVICE_ID}/ca/private-key-password',
            body=key_password
        )

    def tearDown(self):
        super().load_default_policy()

    def test_sign_201_json(self):
        """Test case for 201 JSON response when requesting a signed certificate
        The default response to a successful request is a JSON response body
        with a `certificate` field including the signed certificate
        """
        response, status, _ = self.api.sign_with_http_info(
            self.account,
            self.CA_SERVICE_ID,
            self.csr,
            'P1D'
        )

        self.assertEqual(status, 201)
        self.assertIsInstance(response, conjur.models.certificate_json.CertificateJson)

        self.assertEqual(response.certificate[:27], '-----BEGIN CERTIFICATE-----')

    @unittest.expectedFailure
    def test_sign_201_pem(self):
        """Test case for 201 PEM response when requesting a signed certificate
        When the `Accept` header is set to `application/x-pem-file`, the request body
        is a PEM encoded certificate

        This test case fails due to an issue in the OpenAPI Generator
        with passing an `Accept` header. The generator overwrites any assignment to `Accept`.
        """
        response, status, _ = self.api.sign_with_http_info(
            self.account,
            self.CA_SERVICE_ID,
            self.csr,
            'P1D',
            accept='application/x-pem-file'
        )

        self.assertEqual(status, 201)
        self.assertIsInstance(response, str)

    def test_sign_with_encrypted_key_201(self):
        """Test case for 201 response when requesting a signed certificate
        Uses an encrypted intermediate key and password to sign CSR
        """
        key_password = read_file(KEY_PASSWORD_PATH)
        encrypted_key = read_file(ENCRYPTED_KEY_PATH)

        self.update_ca_private_key(encrypted_key)
        self.update_ca_key_password(key_password)

        response, status, _ = self.api.sign_with_http_info(
            self.account,
            self.CA_SERVICE_ID,
            self.csr,
            'P1D'
        )

        self.assertEqual(status, 201)
        self.assertIsInstance(response, conjur.models.certificate_json.CertificateJson)

        self.assertEqual(response.certificate[:27], '-----BEGIN CERTIFICATE-----')

    def test_sign_with_encrypted_key_500(self):
        """Test case for 500 response when requesting a signed certificate
        500 status repsonses can result from a misconfigured CA service
        In this test, the Conjur variable for the encrypted key's password is incorrect
        """
        encrypted_key = read_file(ENCRYPTED_KEY_PATH)

        self.update_ca_private_key(encrypted_key)
        self.update_ca_key_password('wrong_pass')

        with self.assertRaises(conjur.ApiException) as context:
            self.api.sign(
                self.account,
                self.CA_SERVICE_ID,
                self.csr,
                'P1D'
            )

        self.assertEqual(context.exception.status, 500)

    def test_sign_400(self):
        """Test case for 400 response when requesting a signed certificate
        Error originates from NGINX, occurs when making HTTPS requests to Conjur through NGINX
        This same request made directly to Conjur with HTTP results in a 422 status response
        400 - request rejected by NGINX proxy
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.sign(
                self.account,
                '\00',
                self.csr,
                'P1D'
            )

        self.assertEqual(context.exception.status, 400)

    def test_sign_401(self):
        """Test case for 401 response when requesting a signed certificate
        401 - unauthorized request
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.bad_auth_api.sign(
                self.account,
                self.CA_SERVICE_ID,
                self.csr,
                'P1D'
            )

        self.assertEqual(context.exception.status, 401)

    def test_sign_403a(self):
        """Test case A for 403 response when requesting a signed certificate
        Conjur responds with 403 status when the authenticated role is not a Host
        """
        user_api = conjur.CertificateAuthorityApi(self.client)

        with self.assertRaises(conjur.ApiException) as context:
            user_api.sign(
                self.account,
                self.CA_SERVICE_ID,
                self.csr,
                'P1D'
            )

        self.assertEqual(context.exception.status, 403)

    def test_sign_403b(self):
        """Test case B for 403 response when requesting a signed certificate
        Conjur responds with 403 status when the authenticated host does not have
        `sign` privilege on the CA service
        """
        no_sign_client = api_config.get_api_client(
            'signing-service/no-sign-client',
            'host'
        )
        no_sign_api = conjur.CertificateAuthorityApi(no_sign_client)

        with self.assertRaises(conjur.ApiException) as context:
            no_sign_api.sign(
                self.account,
                self.CA_SERVICE_ID,
                self.csr,
                'P1D'
            )

        self.assertEqual(context.exception.status, 403)

    @unittest.expectedFailure
    def test_sign_403c(self):
        """Test case C for 403 response when requesting a signed certificate
        Conjur responds with 403 status when the CSR Common Name does not
        match the ID of the authenticated host
        """
        cn_test_client = api_config.get_api_client(
            'signing-service/cn-test-client',
            'host'
        )
        cn_test_api = conjur.CertificateAuthorityApi(cn_test_client)

        with self.assertRaises(conjur.ApiException) as context:
            cn_test_api.sign(
                self.account,
                self.CA_SERVICE_ID,
                self.csr,
                'P1D'
            )

        self.assertEqual(context.exception.status, 403)

    def test_sign_404(self):
        """Test case for 404 response when requesting a signed certificate
        404 - the requested CA service was not found
        """
        with self.assertRaises(conjur.ApiException) as context:
            self.api.sign(
                self.account,
                'fakeService',
                self.csr,
                'P1D'
            )

        self.assertEqual(context.exception.status, 404)

    @unittest.skipIf(api_config.ENTERPRISE_TESTS,
             "Our Enterprise conf doesn't support bypassing ssl so we cannot evoke this response")
    def test_sign_422(self):
        """Test case for 422 response when requesting a signed certificate
        422 - Conjur received a malformed parameter
        """
        self.api.api_client.configuration.host = 'http://conjur'
        with self.assertRaises(conjur.ApiException) as context:
            self.api.sign(
                self.account,
                '\00',
                self.csr,
                'P1D'
            )

        self.assertEqual(context.exception.status, 422)

if __name__ == '__main__':
    unittest.main()
