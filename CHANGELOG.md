# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [5.3.0] - 2021-12-22

### Added
- Add new route for enabling authenticator with default service
  [cyberark/conjur-openapi-spec#215](https://github.com/cyberark/conjur-openapi-spec/pull/215)

## [5.2.0] - 2021-09-08
### Added
- New JWT authenticator endpoints have been added to the spec.
  [cyberark/conjur-openapi-spec#193](https://github.com/cyberark/conjur-openapi-spec/pull/193)

### Fixed
- Request body details for secret creation so all clients can properly set secrets. This changes
  the MIME type of the request body to `application/octet-stream` in place of text plain,
  allowing for proper binary secrets in clients (`format: binary` is broken in some clients).
  [cyberark/conjur-openapi-spec#187](https://github.com/cyberark/conjur-openapi-spec/pull/187)
- Authentication methods not requiring any API authentication (conjurAuth, basicAuth, etc) now
  specify an empty list as the `security` field ensuring utilities dont assume all authentication
  types are valid.
  [cyberark/conjur-openapi-spec#196](https://github.com/cyberark/conjur-openapi-spec/pull/196)

### Changed
- Consolidate `bin/integration_test` and `bin/test_enterprise` into `bin/test_integration`.
  Renamed `bin/api_test` to `bin/test_api_contract` and `bin/start` to `bin/dev` to maintain
  repository- and company-wide script convention.
  [cyberark/conjur-openapi-spec#166](https://github.com/cyberark/conjur-openapi-spec/issues/166)
- Remove Bad Gateway error code from authn-oidc error codes following [cyberark/conjur#2360](https://github.com/cyberark/conjur/pull/2360)
  [cyberark/conjur-openapi-spec#204](https://github.com/cyberark/conjur-openapi-spec/pull/204)

## [5.1.1] - 2021-04-28
### Added
- DAP endpoints and scripts to run tests against a DAP instance.
  [cyberark/conjur-openapi-spec#144](https://github.com/cyberark/conjur-openapi-spec/issues/144)
- Basic Java client integration tests and configuration.
  [cyberark/conjur-openapi-spec#181](https://github.com/cyberark/conjur-openapi-spec/pull/181)
- New return code (406) in batch secrets request for when a binary secret is requested
  without specifying a valid `Accept-Encoding` header.
  [cyberark/conjur-openapi-spec#186](https://github.com/cyberark/conjur-openapi-spec/pull/186)

## 5.1.0 - 2021-04-12
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
- Instructions and scripts for using the API spec with Postman included.
  [cyberark/conjur-openapi-spec#92](https://github.com/cyberark/conjur-openapi-spec/issues/92)
- New header parameter allowing user to set request IDs for all endpoints.
  [cyberark/conjur-openapi-spec#175](https://github.com/cyberark/conjur-openapi-spec/issues/175)

### Fixed
- Workaround for request body issue on revokeHostToken operation is now removed and tests have been updated.
  [cyberark/conjur-openapi-spec#52](https://github.com/cyberark/conjur-openapi-spec/issues/52)
- Workaround for request body issue on createSecret operation is now removed and tests have been updated.
  [cyberark/conjur-openapi-spec#105](https://github.com/cyberark/conjur-openapi-spec/issues/105)

### Changed
- Operation names have been updated to match better with existing integrations and documentation.
  [cyberark/conjur-openapi-spec#36](https://github.com/cyberark/conjur-openapi-spec/issues/36)
  [cyberark/conjur-openapi-spec#129](https://github.com/cyberark/conjur-openapi-spec/issues/129)
- Response schemas are now more fully defined and methods will now return pre-defined objects.
  [cyberark/conjur-openapi-spec#43](https://github.com/cyberark/conjur-openapi-spec/issues/43)
- Renamed the `start_editor` script to `start_spec_ui` and updated it to open the bundled version of the spec.
  [cyberark/conjur-openapi-spec#168](https://github.com/cyberark/conjur-openapi-spec/issues/168)
- Updated naming and added support for environment variables in generated Ruby client.
  [cyberark/conjur-openapi-spec#91](https://github.com/cyberark/conjur-openapi-spec/issues/91)

[Unreleased]: https://github.com/cyberark/conjur-openapi-spec/compare/v5.3.0...HEAD
[5.3.0]: https://github.com/cyberark/conjur-openapi-spec/compare/v5.2.0...v5.3.0
[5.2.0]: https://github.com/cyberark/conjur-openapi-spec/compare/v5.1.1...v5.2.0
[5.1.1]: https://github.com/cyberark/conjur-openapi-spec/compare/v5.1.0...v5.1.1
