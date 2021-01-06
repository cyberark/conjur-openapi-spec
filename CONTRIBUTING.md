# Contributing

Please see our [Community Repository](https://github.com/cyberark/community) and our [Contribution Guidelines](https://github.com/cyberark/community/blob/master/Conjur/CONTRIBUTING.md).  
They provide information regarding the process of contributing to Conjur OSS projects,  
including issue reporting, pull request workflow and community guidelines.

* [Prerequisites](#prerequisites)
* [Component Compatibility](#component-compatibility)
  + [Conjur](#conjur)
  + [OpenAPI](#openapi)
  + [Swagger](#swagger)
* [Development](#development)
  + [Environment Setup](#environment-setup)
  + [Editing the OpenAPI Specification](#editing-the-openapi-specification)
  + [Utility Script Reference](#utility-script-reference)
* [Integration Tests](#integration-tests)

<!--
Table of contents generated with markdown-toc
http://ecotruct-canada.github.io/markdown-toc/
-->

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

## Development

### Environment Setup

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
Import the [`openapi.yml`](openapi.yml) into the UI to view/edit.

The environment can be stopped and removed using the `stop` script.

```shell
$ ./bin/stop
```

### Editing the OpenAPI Specification

1. [Start Swagger Editor](#environment-setup)
2. Import the specification YAML into the editor
    * `File` > `Import file`
3. Edit the document as necessary
4. Download the new specification YAML from the editor
    * `File` > `Save as YAML`
5. Overwrite [`openapi.yml`](openapi.yml) with the downloaded YAML file

After editing the OpenAPI spec, it's important to test your changes using `bin/api_test`.

### Utility Script Reference

`bin/api_test [-e <endpoint>]`
* Runs containerized contract testing on all endpoints specified in [`openapi.yml`](openapi.yml)
* Specifying an endpoint with the `-e|--endpoint` flag runs contract tests on that endpoint alone.

`bin/generate_client <language>`
* Generates a client library for the desired `<language>`.  
* Running the script with no argument will generate a Python client by default.

`bin/integration_tests`
* Used to run the suite of integration tests.  
* Stands up a new `docker-compose` environment, and runs the integration tests in a designated container.

`bin/start`
* Used to set up a new development environment.  
* Stands up a new instance of Conjur, and starts a Swagger Editor container.

`bin/start_conjur`
* Used to start a new local Conjur instance based on the project's `docker-compose`.

`bin/start_editor`
* Used to start a Swagger Editor container independent of a Conjur instance.  

`bin/stop`
* Used to deconstruct the development environmnet.  
* Stops and removes the `docker-compose` environment and Swagger Editor.

## Integration Tests

Run the current suite of integration tests using the script:

```shell
$ ./bin/integration_tests
```

## Manual Testing

You can access a compatible version of the the Conjur command line interface by starting the `cli` docker compose container

```shell
$ ./bin/cli
```
