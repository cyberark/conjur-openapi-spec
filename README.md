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

## Contributing

We welcome contributions of all kinds to the Conjur OpenAPI Spec. For instructions on how to  
get started and descriptions of our development workflows, please see our [contributing guide](CONTRIBUTING.md).

## License

This project is [licensed under Apache License v2.0](LICENSE).

Copyright (c) 2020 CyberArk Software Ltd. All rights reserved.
