# Conjur OpenAPI Specification
[![Integration Tests](https://github.com/conjurinc/conjur-openapi-spec/workflows/Integration%20Tests/badge.svg)](https://github.com/conjurinc/conjur-openapi-spec/actions?query=workflow%3A%22Run+Integration+Tests%22)
![](https://img.shields.io/badge/Certification%20Level-Community-28A745?link=https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md)  
This project contains the OpenAPI v3 specification for [Conjur OSS](https://www.conjur.org/).  

---

#### **WARNING: This project is a work in progress, and all code is subject to breaking changes!**

---

The Conjur OpenAPI Specification describes endpoints in the Conjur API via the industry-standard  
OpenAPI v3. The specification can be used to auto-generate client code and documentation to  
streamline development processes.

Find [more from CyberArk](https://github.com/cyberark).

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

## Getting Started

To generate a client library using the OpenAPI spec, use the provided script:

```shell
$ ./bin/generate_client <language>
```

The script will generate a Python client in the absence of a `<language>` argument.  
A full list of supported languages can be found in 
[OpenAPI Generator documentation](https://github.com/OpenAPITools/openapi-generator#overview).


## Examples

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
- Generate an OpenAPI client with `./bin/generate_client <language>` (if not already present)
- Spin up the a Conjur environment from `docker-compose` (if not already present)
- Perform language-specific environment setup
- Run the example

## Contributing

We welcome contributions of all kinds to the Conjur OpenAPI Spec. For instructions on how to  
get started and descriptions of our development workflows, please see our [contributing guide](CONTRIBUTING.md).

## License

This project is [licensed under Apache License v2.0](LICENSE).

Copyright (c) 2020 CyberArk Software Ltd. All rights reservede
