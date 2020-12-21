
import pathlib
import os
import unittest

import openapi_client

CERT_DIR = pathlib.Path('config/https')
SSL_CERT_FILE = 'ca.crt'
CONJUR_CERT_FILE = 'conjur.crt'
CONJUR_KEY_FILE = 'conjur.key'

# Environment Constants
CONJUR_AUTHN_API_KEY = 'CONJUR_AUTHN_API_KEY'
CONJUR_AUTHN_LOGIN = 'CONJUR_AUTHN_LOGIN'
CONJUR_ACCOUNT = 'CONJUR_ACCOUNT'

def get_default_policy():
    """Gets the default testing policy"""
    with open(pathlib.Path('.').resolve() / 'test/config/policy.yaml', 'r') as default_policy:
        return default_policy.read()

def get_api_config():
    """Gets a default API config to be used with the testsing setup"""
    config = openapi_client.Configuration(
            host='https://conjur-https',
        )

    config.ssl_ca_cert = CERT_DIR.joinpath(SSL_CERT_FILE)
    config.cert_file = CERT_DIR.joinpath(CONJUR_CERT_FILE)
    config.key_file = CERT_DIR.joinpath(CONJUR_KEY_FILE)
    config.username = os.environ[CONJUR_AUTHN_LOGIN]
    return config

def get_api_client():
    """Gets an authenticated ApiClient to be used with the testing setup"""
    api_key = os.environ[CONJUR_AUTHN_API_KEY]
    account = os.environ[CONJUR_ACCOUNT]

    config = get_api_config()

    client = openapi_client.ApiClient(config)
    auth = openapi_client.api.AuthnApi(client)
    new_key = auth.authenticate(
            account,
            os.environ['CONJUR_AUTHN_LOGIN'],
            api_key,
            accept_encoding='base64'
        )
    client.configuration.api_key = {'Authorization': f'Token token="{new_key}"'}
    return client

class ConfiguredTest(unittest.TestCase):
    """Meant for test classes to inherit. Sets up an authenticated api client
    for the test to use"""
    @classmethod
    def setUpClass(cls):
        cls.account = os.environ[CONJUR_ACCOUNT]

        cls.client = get_api_client()

    @classmethod
    def tearDownClass(cls):
        # reload the default policy so tests dont interfere with eachother
        default_policy = get_default_policy()
        policy_api = openapi_client.api.policies_api.PoliciesApi(cls.client)
        policy_api.load_policy(cls.account, 'root', default_policy)

        cls.client.close()
