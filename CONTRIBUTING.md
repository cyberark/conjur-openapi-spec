# Contributing

## Table of Contents

- [Prerequisites](#prerequisites)
- [Component Compatibility](#component-compatibility)
- [Set Up a Development Environment](#set-up-a-development-environment)
- [Pull Request Workflow](#pull-request-workflow)

## Prerequisites

Contributing to this repository requires installation of some developer tools.

1. [git][get-git] to manage source code
1. [Docker][get-docker] to manage dependencies and runtime environments
1. [Docker Compose][get-docker-compose] to orchestrate Docker environments
1. Access to DockerHub

[get-git]: https://git-scm.com/downloads
[get-docker]: https://docs.docker.com/engine/installation
[get-docker-compose]: https://docs.docker.com/compose/install

## Component Compatibility

### Conjur

[Conjur OSS v1.9+](https://github.com/cyberark/conjur)

### OpenAPI

[OpenAPI Specification v3.0.0](https://github.com/OAI/OpenAPI-Specification/tree/3.0.0)  
[OpenAPI Generator v4.3.1](https://github.com/OpenAPITools/openapi-generator/tree/v4.3.1)

### Swagger

[Swagger Editor v3.14.6](https://github.com/swagger-api/swagger-editor/tree/v3.14.6)

## Set Up a Development Environment

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

## Editing the OpenAPI Specification

1. [Start Swagger Editor](#set-up-a-development-environment)
1. Import the spec into the UI
1. Edit the document as necessary
1. Download the YAML from the UI
1. Overwrite [`conjur-openapi.yml`](conjur-openapi.yml) with the downloaded yaml file

## Pull Request Workflow

1. Search the [open issues](../../issues) in GitHub to find out what has been planned
1. Select an existing issue or open an issue to propose changes or fixes
1. Add any relevant labels as you work on it
1. Run tests as described [in the main README](https://github.com/conjurinc/conjur-api-python3#testing),
ensuring they pass
1. Submit a pull request, linking the issue in the description
1. Adjust labels as-needed on the issue. Ask another contributor to review and merge your code if there are delays in merging.
