# Spec-Generated Ruby API Client Example

This example is meant to give an example use case for OpenAPI spec generated clients.  
It covers using some of the most popular Conjur OSS endpoints with Ruby:
- Authenticate a user
- Change user's own password
- Rotate user's API key
- Load the root policy
- Store and retrieve a secret

The example uses [RVM](https://rvm.io/) to manage Ruby versions and Gemsets.

The `run` script is responsible for executing the example by environment-conscious means by:
- Ensuring that RVM is installed
- If needed, generating a new Ruby client from the OpenAPI spec
- If needed, spinning up a new `docker-compose` environment
- Building a gem from the Ruby client
- Creating a new RVM Gemset, and installing the client gem and its dependencies
- Running the example with the new Gemset

Documentation regarding format and use of OpenAPI client instances and their functions is  
generated with the client, and can be found in the `docs` folder of the client library.
