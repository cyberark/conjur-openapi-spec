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

The script with generate a Python client in the absence of a `<language>` argument.  
A full list of supported languages can be found in [OpenAPI Generator documentation](https://github.com/OpenAPITools/openapi-generator#overview).


## Generated Client Example

Included in the `examples` directory is a demonstration use case.  
The demo shows how to use popular Conjur API endpoints with a spec-generated Python client:
- Authenticate a user
- Change user's own password
- Rotate user's API key
- Load the root policy
- Store and retrieve a secret

To run the demo, start a development environment and generate a Python client.

```shell
$ ./bin/start
$ ./bin/generate_client
```

Install dependencies for the OpenAPI spec generated client.

```shell
$ cd out/python; python3 setup.py install; cd ../..
```

Store the admin's API key as an environment variable, and run the client demo.

```shell
$ export CONJUR_ADMIN_API_KEY="$(docker-compose exec conjur conjurctl role retrieve-key dev:user:admin | tr -d '\r')"
$ ./examples/python_client.py
```

It is important to note that after the demo is run, the environment variable containing the admin  
API key is out-of-date. To maintain the variable, it should be retrieved again from Conjur.

## Contributing

We welcome contributions of all kinds to the Conjur OpenAPI Spec. For instructions on how to  
get started and descriptions of our development workflows, please see our [contributing guide](CONTRIBUTING.md).

## License

This project is [licensed under Apache License v2.0](LICENSE.md)
