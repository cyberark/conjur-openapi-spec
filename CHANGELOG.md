# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Example use case of spec-generated Ruby client. 
  [cyberark/conjur-openapi-spec#12](https://github.com/cyberark/conjur-openapi-spec/issues/12)
- The `/whoami` endpoint is now included in the spec. Allows for requesting info about the current client.
  [cyberark/conjur-openapi-spec#56](https://github.com/cyberark/conjur-openapi-spec/issues/56)
- Authenticator status endpoint is now included in the spec file. Allows checking if certain authenticators are working.
  [cyberark/conjur-openapi-spec#59](https://github.com/cyberark/conjur-openapi-spec/issues/59)
- `/resources` endpoint now included in the OpenAPI specification.
  [cybeark/conjur-openapi-spec#62](https://github.com/cyberark/conjur-openapi-spec/issues/62)
- The authenticators index endpoint is now included in the spec file. Allows users to check which authenticators are installed and enabled.
  [cyberark/conjur-openapi-spec#58](https://github.com/cyberark/conjur-openapi-spec/issues/58)
- Secrets endpoint will now except `expirations` as an extra kwarg. Allows for resetting the expiration date of a secret.
  [cybeark/conjur-openapi-spec#64](https://github.com/cyberark/conjur-openapi-spec/issues/64)
- Secrets endpoint integration tests are now fully enumerated
  [cyberark/conjur-openapi-spec#102](https://github.com/cyberark/conjur-openapi-spec/issues/102)
- Adding and deleting role members now supported in Roles spec file.
  [cyberark/conjur-openapi-spec#65](https://github.com/cyberark/conjur-openapi-spec/issues/65)
- `memberships` query parameter supported on Roles endpoint.
  [cybeark/conjur-openapi-spec#67](https://github.com/cyberark/conjur-openapi-spec/issues/67)
- `all` query parameter supported on Roles endpoint.
  [cybeark/conjur-openapi-spec#68](https://github.com/cyberark/conjur-openapi-spec/issues/68)
- The roles `graph` query parameter is now included in the spec file. Allows for viewing a role as a graph/tree.
  [cyberark/conjur-openapi-spec#69](https://github.com/cyberark/conjur-openapi-spec/issues/69)
- Generic authenticator endpoint that covers most Conjur platform authenticators.
  [cyberark/conjur-openapi-spec#74](https://github.com/cyberark/conjur-openapi-spec/issues/74)
  [cyberark/conjur-openapi-spec#70](https://github.com/cyberark/conjur-openapi-spec/issues/70)
  [cyberark/conjur-openapi-spec#75](https://github.com/cyberark/conjur-openapi-spec/issues/75)
- Endpoint to configure enabled Conjur authenticators via the API.
  [cyberark/conjur-openapi-spec#66](https://github.com/cyberark/conjur-openapi-spec/issues/66)
- `/ca/` endpoint now included in the OpenAPI specification.
  [cyberark/conjur-openapi-spec#63](https://github.com/cyberark/conjur-openapi-spec/issues/63)
- OIDC authenticate endpoint now included in the OpenAPI specification. Users can now authenticate with Conjur through an OIDC provider using a generated client.
  [cyberark/conjur-openapi-spec#60](https://github.com/cyberark/conjur-openapi-spec/issues/60)
- Google Cloud Provider authenticate endpoint now included in the spec file. Users can now authenticate with Conjur using GCP.
  [cyberark/conjur-openapi-spec#61](https://github.com/cyberark/conjur-openapi-spec/issues/61)
- New options to `generate_client` script for greater control over generated output.
- `/authn-k8s/:service_id/inject_client_cert` endpoint now included in the OpenAPI specification.
  [cyberark/conjur-openapi-spec#3](https://github.com/cyberark/conjur-openapi-spec/issues/3)
- Basic C#/.NET client tests and generation templates are now included in the project.
  [cyberark/conjur-openapi-spec#94](https://github.com/cyberark/conjur-openapi-spec/issues/94)
- Optional Accept-Encoding header parameter now included in secrets batch endpoint.
  [cyberark/conjur-openapi-spec#145](https://github.com/cyberark/conjur-openapi-spec/issues/145)
