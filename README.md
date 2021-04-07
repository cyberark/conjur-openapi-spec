# Conjur OpenAPI Specification
[![Integration Tests](https://github.com/conjurinc/conjur-openapi-spec/workflows/Integration%20Tests/badge.svg)](https://github.com/conjurinc/conjur-openapi-spec/actions?query=workflow%3A%22Run+Integration+Tests%22)
![](https://img.shields.io/badge/Certification%20Level-Community-28A745?link=https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md)  
[![Maintainability](https://api.codeclimate.com/v1/badges/7bf3957dc33055b0de06/maintainability)](https://codeclimate.com/github/cyberark/conjur-openapi-spec/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/7bf3957dc33055b0de06/test_coverage)](https://codeclimate.com/github/cyberark/conjur-openapi-spec/test_coverage)

This project contains the OpenAPI v3 specification for [Conjur OSS](https://www.conjur.org/).  

---

#### **WARNING: This project is a work in progress, and all code is subject to breaking changes!**

---

The Conjur OpenAPI Specification describes endpoints in the Conjur API via the industry-standard  
OpenAPI v3. The specification can be used to auto-generate client code and documentation to  
streamline development processes.

Find [more from CyberArk](https://github.com/cyberark).

* [Api Documentation](https://github.com/cyberark/conjur-openapi-spec/wiki)
* [Requirements](#requirements)
* [Getting Started](#getting-started)
* [Contributing](#contributing)
* [License](#license)

<!--
Table of contents generated with markdown-toc
http://ecotruct-canada.github.io/markdown-toc/
-->

## Requirements

This project requires Docker and access to DockerHub.

The OpenAPI Specification is compatible with [Conjur OSS v1.9+](https://github.com/cyberark/conjur).  
Clients are generated using [OpenAPI Generator v4.3.1](https://github.com/OpenAPITools/openapi-generator/tree/v4.3.1).

### Use With Dynamic Access Provider (DAP)

The Conjur API endpoints included in this spec are a subset of DAP's endpoints,
for that reason this API specification (and by extension any generated
clients/documentation) can be used with DAP.

The following is a list of endpoints present in DAP but absent from this spec:

* `/health`
* `/remote_health`
* `/configuration/{account}/seed/follower`
* `/info`

## Getting Started

If you are new to OpenAPI you may want to visit the
[understanding the spec](https://github.com/cyberark/conjur-openapi-spec/wiki/Interpreting-The-Spec)
wiki page, which will give you a brief overview of how to interpret and make changes to the spec file.

To view the Conjur OpenAPI Specification directly, please see the [spec/](./spec/) directory.

In the sections below, we review some of the ways you can leverage the spec in your own workflows.
Need help with something that's not yet documented here? Please
[open an issue](https://github.com/cyberark/conjur-openapi-spec/issues/new/choose) - we'd be happy
to help you get started.

### Swagger Editor

The [Swagger Editor](https://swagger.io/tools/swagger-ui/) is a great tool for viewing and editing
OpenAPI specifications, although we discourage editing directly in the UI because our spec
is split over multiple files. In order to view the spec in Swagger run the
`./bin/start_spec_ui` script, all of the standard spec files will be bundled together and
an instance of the UI will be opened pointing at the bundled spec.

### Generating client libraries

To generate a client library using the OpenAPI spec, use the provided script:

```shell
$ ./bin/generate_client -l <language> [-o <output-dir>]
```

The script will generate a Python client in the absence of a `<language>` argument.  
A full list of supported languages can be found in 
[OpenAPI Generator documentation](https://github.com/OpenAPITools/openapi-generator#overview).


#### Examples

Included in the `examples` directory are demonstrations for using spec-generated API clients.  
The demos show how to use popular Conjur API endpoints:
- Authenticate a user
- Change user's own password
- Rotate user's API key
- Load the root policy
- Store and retrieve a secret

There are currently examples in two languages, Python and Ruby.  
The examples can be run using their respective scripts:

```shell
$ ./examples/python/start
$ ./examples/ruby/start
```

Each example performs the following steps:
- Generate an OpenAPI client with `./bin/generate_client -l <language>` (if not already present)
- Spin up the a Conjur environment from `docker-compose` (if not already present)
- Perform language-specific environment setup
- Run the example

### Exploring the Conjur API with Postman

A step-by-step guide can be found in the [`examples/postman`](examples/postman) directory.

### Using the OpenAPI spec with API Gateways

Because the OpenAPI Specification is a widely accepted standard interface for RESTful APIs, many
popular API gateways have tools for importing an OpenAPI spec into their service.

Included in this project is an example of using Kong Gateway OSS with Conjur. Importing an
OpenAPI spec into Kong requires first converting it into a Kong declarative configuration, which
can be done with script `bin/generate_kong_config`. The example can be run with
`examples/kong/start`.

Apigee Edge has a convenient and well-documented
[process](https://docs.apigee.com/api-platform/tutorials/create-api-proxy-openapi-spec)
for creating an API proxy from an OpenAPI Specification, but requires the spec to define a public
[target server](https://swagger.io/docs/specification/api-host-and-base-path/).

While AWS API Gateway provides a
[workflow](https://docs.aws.amazon.com/apigateway/latest/developerguide/import-edge-optimized-api.html)
for setting up a new API by importing an OpenAPI spec, there are many OpenAPI features that are
[not supported](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-known-issues.html).
This precludes this project from being completely compatible.

## Contributing

We welcome contributions of all kinds to the Conjur OpenAPI Spec. For instructions on how to  
get started and descriptions of our development workflows, please see our [contributing guide](CONTRIBUTING.md).

## License

This project is [licensed under Apache License v2.0](LICENSE).

Copyright (c) 2020 CyberArk Software Ltd. All rights reserved.
