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


## Examples

Included in the `examples` directory is a generated API client demonstration.  
The demo shows how to use popular Conjur API endpoints with a spec-generated client:
- Authenticate a user
- Change user's own password
- Rotate user's API key
- Load the root policy
- Store and retrieve a secret

### Creating and Using a Python API Client

The Python client example can be run easily using the provided script:

```shell
$ ./examples/python/run
```

The example workflow is described below.

In order to run the demo, you must have first generated a Python client, and  
have a live Conjur server to interface with. This can be done using the following:

```shell
$ ./bin/generate_client
$ ./bin/start_conjur
```

Setup a Python virtual environment and install dependencies for the OpenAPI spec generated client.

```shell
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip3 install -e out/python
```

Store the Conjur admin's API key as an environment variable, and run the client demo.

```shell
$ export CONJUR_ADMIN_API_KEY="$(docker-compose exec conjur conjurctl role retrieve-key dev:user:admin | tr -d '\r')"
$ ./examples/python/python_client.py
```

To deactivate the Python virtual environment, input `deactivate` to an environment-active shell.

```shell
(venv) $ deactivate
```

## Contributing

We welcome contributions of all kinds to the Conjur OpenAPI Spec. For instructions on how to  
get started and descriptions of our development workflows, please see our [contributing guide](CONTRIBUTING.md).

## License

This project is [licensed under Apache License v2.0](LICENSE).

Copyright (c) 2020 CyberArk Software Ltd. All rights reservede
