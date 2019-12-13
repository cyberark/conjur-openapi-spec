# draft-conjur-openapi-spec

This project contains the OpenAPI v3 spec for [Conjur OSS](https://www.conjur.org/) and DAP.

---

### **Status**: Alpha

#### **Warning: All code is subject to breaking changes!**

---

# Development

## Requirements

This project requires Docker and access to DockerHub

## Running

```shell
$ ./bin/start_editor
```

A browser window will be opened to the container running Swagger UI.

Import the [`conjur-openapi.yml`](conjur-openapi.yml) into the UI to view/edit.

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
