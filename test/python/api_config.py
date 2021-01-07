
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

WEBSERVICE_POLICY = pathlib.Path('test/config/webservice.yml')

def get_webservice_policy():
    """Gets the text for the webservice testing policy"""
    with open(WEBSERVICE_POLICY, 'r') as policy:
        return policy.read()


def get_default_policy():
    """Gets the default testing policy"""
    with open(pathlib.Path('.').resolve() / 'test/config/policy.yaml', 'r') as default_policy:
        return default_policy.read()

def get_bad_auth_api_config(username='admin'):
    """Gets a default API config to be used with the testsing setup with no password
    specified"""
    config = get_api_config(username=username)
    config.password = None
    return config

def get_api_config(username='admin'):
    """Gets a default API config to be used with the testsing setup"""
    config = openapi_client.Configuration(
            host='https://conjur-https',
        )

    config.ssl_ca_cert = CERT_DIR.joinpath(SSL_CERT_FILE)
    config.cert_file = CERT_DIR.joinpath(CONJUR_CERT_FILE)
    config.key_file = CERT_DIR.joinpath(CONJUR_KEY_FILE)
    config.username = username
    return config

def get_api_key(username):
    """Gets the api key for a given username"""
    if username == 'admin':
        return os.environ[CONJUR_AUTHN_API_KEY]
    auth_api = openapi_client.api.authn_api.AuthnApi(get_api_client())
    api_key = auth_api.rotate_api_key('authn', os.environ[CONJUR_ACCOUNT], role=f'user:{username}')
    return api_key

def get_api_client(username='admin'):
    """
    Gets an authenticated ApiClient with the given
    username/password to be used with the testing setup
    """
    api_key = get_api_key(username)
    account = os.environ[CONJUR_ACCOUNT]

    config = get_api_config()

    client = openapi_client.ApiClient(config)
    auth = openapi_client.api.AuthnApi(client)
    api_token = auth.authenticate(
            'authn',
            account,
            username,
            api_key,
            accept_encoding='base64'
        )
    client.configuration.api_key = {'Authorization': f'Token token="{api_token}"'}
    return client

class ConfiguredTest(unittest.TestCase):
    """Meant for test classes to inherit. Sets up an authenticated api client
    for the test to use"""
    @classmethod
    def setUpClass(cls):
        cls.account = os.environ[CONJUR_ACCOUNT]

        cls.client = get_api_client()
        cls.bad_auth_client = openapi_client.ApiClient(get_api_config())

    @classmethod
    def tearDownClass(cls):
        # reload the default policy so tests dont interfere with eachother
        cls.load_default_policy()

        cls.client.close()

    @classmethod
    def load_default_policy(cls):
        """Reloads a default policy
        Compartmentalizes test cases by replacing any loaded policy
        """
        default_policy = get_default_policy()
        policy_api = openapi_client.api.policies_api.PoliciesApi(cls.client)
        policy_api.load_policy(cls.account, 'root', default_policy)
