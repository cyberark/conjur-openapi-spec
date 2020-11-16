# Conjur/DAP OpenAPI Spec

This project contains the OpenAPI v3 specification for [Conjur OSS](https://www.conjur.org/) and DAP v10+.

---

### **Status**: Alpha

#### **Warning: All code is subject to breaking changes!**

---

# Development

## Requirements

This project requires Docker and access to DockerHub

## Environment Setup

Setup the development environment using the `start` script. The script starts a Swagger UI 
container, used to the edit the OpenAPI spec, and stands up a new instance of Conjur to test the 
spec against.

```shell
$ ./bin/start
```

To use the OpenAPI spec against a pre-existing Conjur server, start the Swagger UI editor with 
the `start_editor` script.

```shell
$ ./bin/start_editor
```

In each case, a browser window will be opened to the container running Swagger UI.
Import the [`conjur-openapi.yml`](conjur-openapi.yml) into the UI to view/edit.

The environment can be stopped and removed using the `stop` script.

```shell
$ ./bin/stop
```

## Editing

- Start SwaggerUI
- Import the spec into the UI
- Make needed edits
- Download the YAML from the UI
- Overwrite [`conjur-openapi.yml`](conjur-openapi.yml) with the downloaded yaml file

# Contributing

We store instructions for development and guidelines for how to build and test this
project in the [CONTRIBUTING.md](CONTRIBUTING.md) - please refer to that document
if you would like to contribute.

# License

This project is [licensed under Apache License v2.0](LICENSE.md)
