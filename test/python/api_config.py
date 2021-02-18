
import pathlib
import os
import unittest

import conjur

CONJUR_HOST = os.environ.get('CONJUR_HOST', default='https://conjur-https')
CERT_DIR = pathlib.Path(os.environ.get('CERT_DIR', default='config/https'))
SSL_CERT_FILE = os.environ.get('SSL_CERT_FILE', default='ca.crt')
CONJUR_CERT_FILE = os.environ.get('CONJUR_CERT_FILE', default='conjur.crt')
CONJUR_KEY_FILE = os.environ.get('CONJUR_KEY_FILE', default='conjur.key')

# Environment Constants
CONJUR_AUTHN_API_KEY = 'CONJUR_AUTHN_API_KEY'
CONJUR_AUTHN_LOGIN = 'CONJUR_AUTHN_LOGIN'
CONJUR_ACCOUNT = 'CONJUR_ACCOUNT'

WEBSERVICE_POLICY = pathlib.Path('test/config/webservice.yml')
OIDC_POLICY_FILE = 'test/config/oidc-webservice.yml'

if (ENTERPRISE_TESTS := os.environ.get('ENTERPRISE_TESTS', default=False)) == '1':
    ENTERPRISE_TESTS = True

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
    config = conjur.Configuration(
            host=CONJUR_HOST,
        )
    config.ssl_ca_cert = CERT_DIR.joinpath(SSL_CERT_FILE)
    config.cert_file = CERT_DIR.joinpath(CONJUR_CERT_FILE)
    config.key_file = CERT_DIR.joinpath(CONJUR_KEY_FILE)
    config.username = username
    return config

def get_api_key(username, role):
    """Gets the api key for a given username"""
    if username == 'admin':
        return os.environ[CONJUR_AUTHN_API_KEY]
    auth_api = conjur.api.AuthenticationApi(get_api_client())
    api_key = auth_api.rotate_api_key(
        os.environ[CONJUR_ACCOUNT],
        role=f'{role}:{username}'
    )
    return api_key

def get_api_client(username='admin', role='user'):
    """
    Gets an authenticated ApiClient with the given
    username/password to be used with the testing setup

    When authenticating, host's usernames must be given in the form `host/{id}`
    """
    api_key = get_api_key(username, role)
    account = os.environ[CONJUR_ACCOUNT]

    if role == 'host':
        username = f'host/{username}'

    config = get_api_config()

    client = conjur.ApiClient(config)
    auth = conjur.api.AuthenticationApi(client)
    api_token = auth.get_access_token(
            account,
            username,
            body=api_key,
            accept_encoding='base64'
        )
    client.configuration.api_key = {'Authorization': f'Token token="{api_token}"'}
    return client

def setup_oidc_webservice():
    """Loads a policy for the oidc webservice into conjur"""
    client = get_api_client()
    account = os.environ[CONJUR_ACCOUNT]
    policy_api = conjur.api.PoliciesApi(client)
    with open(OIDC_POLICY_FILE, 'r') as policy_file:
        policy = policy_file.read()
    policy_api.update_policy(account, 'root', policy)

    secrets_api = conjur.api.SecretsApi(client)
    secrets_api.create_secret(
        account,
        'variable',
        'conjur/authn-oidc/test/provider-uri',
        body='https://keycloak:8443/auth/realms/master'
    )
    secrets_api.create_secret(
        account,
        'variable',
        'conjur/authn-oidc/test/id-token-user-property',
        body='preferred_username'
    )

class ConfiguredTest(unittest.TestCase):
    """Meant for test classes to inherit. Sets up an authenticated api client
    for the test to use"""
    @classmethod
    def setUpClass(cls):
        cls.account = os.environ[CONJUR_ACCOUNT]

        cls.client = get_api_client()
        cls.bad_auth_client = conjur.ApiClient(get_api_config())
        cls.load_default_policy()

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
        policy_api = conjur.api.PoliciesApi(cls.client)
        policy_api.replace_policy(cls.account, 'root', default_policy)
