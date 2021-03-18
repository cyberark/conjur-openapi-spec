#!/usr/bin/env ruby
# confirmed for ruby versions 2.6+

# Load the gem
require 'openapi_client'

CERT_DIR = '/config/https'
SSL_CERT_FILE = 'ca.crt'
CONJUR_CERT_FILE = 'conjur.crt'
CONJUR_KEY_FILE = 'conjur.key'

ACCOUNT = "dev"
LOGIN = "admin"
ADMIN_API_KEY = ENV["CONJUR_ADMIN_API_KEY"]
if ADMIN_API_KEY.empty?
  STDERR.puts "Conjur Admin API key Environment Variable not set!"
  STDERR.puts "Use the privided script, or be sure to first execute: "
  STDERR.puts 'export CONJUR_ADMIN_API_KEY="$(docker-compose exec conjur conjurctl role retrieve-key dev:user:admin | tr -d \'\\r\')'
  exit(1)
end

# Constants
new_password = "N3w-Passw0rd!"
secret = "supersecretstuff"
secret_id = "sampleSecret"
empty_policy = IO.read("/config/policy/simple.yml")
policy = IO.read("/config/policy/policy.yml")

# Setup client configuration
config = OpenapiClient.configure
# config.debugging = true
config.scheme = "https"
config.host = "conjur-https"

config.username = LOGIN
config.password = ADMIN_API_KEY

config.verify_ssl = true
config.ssl_ca_cert = File.join(CERT_DIR, SSL_CERT_FILE)
config.cert_file = File.join(CERT_DIR, CONJUR_CERT_FILE)
config.key_file = File.join(CERT_DIR, CONJUR_KEY_FILE)

# Authenticating admin using basicAuth
authn_instance = OpenapiClient::AuthenticationApi.new
token = nil
puts "Authenticating admin..."
token = authn_instance.get_access_token(
  account=ACCOUNT,
  login=LOGIN,
  body=ADMIN_API_KEY,
  opts={accept_encoding: 'base64'}
)
puts "Base64 encoded token: #{token}"

# Change admin password using basicAuth
puts
puts "Changing admin password..."
authn_instance.change_password(
  account=ACCOUNT,
  body=new_password
)
puts "Password change successful."

config.password = new_password

# Add Conjur Token header to api configuration
token_body = 'token="%s"' % [token]
config.api_key['Authorization'] = token_body
config.api_key_prefix['Authorization'] = 'Token'

policy_instance = OpenapiClient::PoliciesApi.new
authn_instance = OpenapiClient::AuthenticationApi.new

# Load empty policy, allows the example to be run multiple times sequentially
# Loading a policy returns data for users CREATED when the policy is loaded. Without loading
# an "empty" policy, if the user alice already exists due to a prior example run, loading
# the full policy will not respond with alice's api key.
puts
puts "Loading empty root policy..."
policy_instance.load_policy(
  account=ACCOUNT,
  identifier="root",
  body=empty_policy
)
puts "Empty policy loaded."

puts
puts "Loading root policy..."
loaded_results = policy_instance.load_policy(
  account=ACCOUNT,
  identifier="root",
  body=policy
)
puts "Policy loaded."

alice_api_key = loaded_results[:created_roles]["dev:user:alice".to_sym][:api_key]
puts "Alice API key: #{alice_api_key}"

# Rotate alice API key as admin, uses conjurAuth
puts
puts "Rotating alice API key..."
alice_api_key = authn_instance.rotate_api_key(
  account=ACCOUNT,
  opts={role: 'user:alice'}
)
puts "New API key: #{alice_api_key}"

# Store a secret, uses conjurAuth
secrets_instance = OpenapiClient::SecretsApi.new
puts
puts "Storing secret..."
puts "Secret data: #{secret}"
secrets_instance.create_variable(
  account=ACCOUNT,
  kind="variable",
  identifier=secret_id,
  opts={body: secret}
)
puts "Secret stored."

# Retrieve a secret, uses conjurAuth
puts
puts "Retrieving secret..."
retrieved_secret = secrets_instance.get_variable(
  account=ACCOUNT,
  kind="variable",
  identifier=secret_id
)
puts "Retrieved secret: #{retrieved_secret}"

if retrieved_secret != secret
  puts "Secret Malformed"
  puts "Secret stored: #{secret}"
  puts "Secret retrieved: #{retrieved_secret}"
  exit(1)
end

puts
puts "Done!"
