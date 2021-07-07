# Spec-Generated Python API Client Example

This example is meant to give an example use case for OpenAPI spec generated clients.
It covers using some of the most popular Conjur Open Source endpoints with Python:
- Authenticate a user
- Change user's own password
- Rotate user's API key
- Load the root policy
- Store and retrieve a secret

The `run` script is responsible for executing the example by environment-conscious means by:
- If needed, generating a new Python client from the OpenAPI spec
- If needed, spinning up a new `docker-compose` environment with Conjur and a Postgres database
- Running the example in a Python Docker container

Documentation regarding format and use of OpenAPI client instances and their functions is
generated with the client, and can be found in the `docs` folder of the client library.
