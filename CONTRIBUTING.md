# Contributing

Please see our [Community Repository](https://github.com/cyberark/community) and our [Contribution Guidelines](https://github.com/cyberark/community/blob/master/Conjur/CONTRIBUTING.md).
They provide information regarding the process of contributing to Conjur Open Source projects,
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
    - [Automated tests](#automated-tests)
    - [Linters](#linters)
    - [Utility scripts](#utility-scripts)
    - [Conjur Enterprise Developers](#conjur-enterprise-developers)
* [Manual Testing](#manual-testing)
* [Releasing](#releasing)
  + [Verify and update dependencies](#verify-and-update-dependencies)
  + [Update the version and changelog](#update-the-version-and-changelog)
  + [Tag the version](#tag-the-version)
  + [Add a new GitHub release](#add-a-new-github-release)
  + [Enterprise Releases](#enterprise-releases)

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

[Conjur Open Source v1.9+](https://github.com/cyberark/conjur)

### OpenAPI

[OpenAPI Specification v3.0.0](https://github.com/OAI/OpenAPI-Specification/tree/3.0.0)
[OpenAPI Generator v4.3.1](https://github.com/OpenAPITools/openapi-generator/tree/v4.3.1)

### Swagger

[Swagger Editor v3.14.6](https://github.com/swagger-api/swagger-editor/tree/v3.14.6)

## Development

### Getting Started

There are two main aspects to this project, the spec itself and the generated clients. Contained in the
`bin` directory there are many scripts for running various tests and checks against both the spec itself
and the generated clients. The most important scripts are `integration_tests` and `generate_client`.

The [`generate_client`](#utility-scripts) script will use the [OpenApi Generator](https://openapi-generator.tech/)
to output a client to the `out` directory. You can specify the generated client's language with the `-l`
option, e.g. `./bin/generate_client -l go`. This is a good tool if you need to generate a client for a currently
unreleased version, or need to do some manual testing on the latest version of a client.

The [`integration_tests`](#automated-tests) script will automatically generate a client then run integration tests against
that client if they are available. Integration tests can be found in the `test` directory, you can
specify the language of the client to test with a long flag: `--python`, `--csharp`. Both scripts also have other
options which can be viewed by running them with the `-h` flag.

There is also an included `api_test` script which will run contract tests against an instance of
Conjur. It is a great tool for finding return codes which are missing from the spec, and for finding
changes in Conjur which may not yet have been reflected in the spec.

For a full list of all scripts and their purpose see the [utility script reference](#utility-script-reference)

### Environment Setup

Setup the development environment using the `start_conjur` script. The script starts a Swagger Editor
container, used to the edit the OpenAPI spec, and stands up a new instance of Conjur to test the
spec against.

```shell
$ ./bin/start_conjur
```

To use the OpenAPI spec against a pre-existing Conjur server, start the Swagger Editor editor with
the `start_spec_ui` script.

```shell
$ ./bin/start_spec_ui
```

In each case, a browser window will be opened to the container running Swagger Editor.
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

Modifications to the spec should go with updated integration tests, which can
be found in `test/python/`. The tests are based on a generated client, so to
see the impact of your spec changes you can generate a Python client using
`./bin/generate_client -l python` and view the generated client in `out/python/`.

To ensure your changes work as expected, you can run the [automated tests](#automated-tests).

### Utility Script Reference

#### Automated tests

`bin/test_api_contract [-e <endpoint>]`
* Uses Schemathesis to generate test cases for API endpoints, which test the
  conformance between Conjur Open Source and the OpenAPI specification.
* Runs containerized contract testing on all endpoints specified in [`openapi.yml`](openapi.yml)
* Specifying an endpoint with the `-e|--endpoint` flag runs contract tests on that endpoint alone.

`bin/test_integration`
* Used to run the suite of integration tests against Conjur Open Source or Enterprise.
* Stands up a new Conjur environment, generates a client
  library, and runs the integration test suite.
* User must specify a client language to test with `-l`:
  ```shell
  $ ./bin/test_integration -l python
  ```
* Run a subset of a clients tests by including an argument with the full package
  path of the tests to run:
  ```shell
  $ ./bin/test_integration -l python --test test_authn_api.TestAuthnApi.test_authenticate_200
  ```
* Tests can be run against Conjur Enterprise.
* This requires access to the CyberArk Docker registry in order to pull Conjur Enterprise images
  ```shell
  $ ./bin/test_integration --enterprise -l python
  ```

#### Linters

`./bin/lint_tests`
* Lints the Python integration tests using Pylint.

`./bin/lint_spec`
* Uses [spectral](https://github.com/stoplightio/spectral) to lint the OpenAPI YAML.
* Will find broken references, malformed objects, and any other errors in the spec itself.

#### Utility scripts

`bin/transform [--enterprise/--oss]`
* Generates a usable version of the specification for either Conjur (--oss) or Conjur Enterprise (--enterprise)
* Generates the Conjur version of the spec by default

`bin/generate_client -l <language> [-o <output-directory>]`
* Generates a client library for the desired `<language>`.
* Running the script with no argument will generate a Python client by default.
* Outputs to the `out` directory by default.

`bin/generate_kong_config`
* Generates a declarative configuration used by Kong Gateway.

`bin/start_spec_ui`
* Used to start a Swagger Editor container independent of a Conjur instance.
* Runs the `bin/bundle_spec` script before starting and points the UI at the bundled spec.
* Editor available at http://localhost:9090 once the container is up.

`bin/dev`
* Used to set up a new development environment.
* Calls both `start_editor` and `start_conjur` to bring up both Conjur and Editor containers.

`bin/start_conjur`
* Used to start a new local Conjur instance based on the project's `docker compose`.
* Both the http & https ports are exposed so requests can be made to Conjur from outside the docker network.

`bin/start_enterprise`
* Used to start a new local Conjur Enterprise instance based on [`conjur-intro`](https://github.com/conjurdemos/conjur-intro)

`bin/stop`
* Used to deconstruct the development environment.
* Stops and removes the `docker compose` environment and Swagger Editor.

`bin/bundle_spec`
* Bundles all the sharded spec files into one file named `spec.yml` in the root project directory.
* It should be noted that this bundled spec file loses some of the names/reference info when bundled and shouldn't
  be used directly to generate a client.

`bin/parse_changelog`
* Parses the changelog and makes sure it is up to date with [keep a changelog](https://keepachangelog.com/en/1.0.0/) standards.

`bin/release`
* Gathers artifacts to be attached to releases of the specification.
* Outputs archives to `release_artifacts` in both zip and tarball format.

#### Conjur Enterprise Developers

The Enterprise only endpoints included in the specification all use a specific annotation to indicate that they
are "enterprise only". When the Open Source version of the spec is generated all of these objects will be removed.

```yaml
someObject:
  x-conjur-settings:
    enterprise-only: true
```

This marks `someObject` as an enterprise only feature.

Note that because all `paths` have to be defined in the `openapi.yml#/paths` object it is
acceptable to just put the annotation on the `openapi.yml#/paths/somePath` object and leave it
off the referenced path definition. In this case when the Open Source version of the spec is generated
the path definition will have had its reference removed thereby not technically being
included in the spec.

Many of the scripts included in the `bin` directory have an optional `--enterprise` flag which
tells the script to use the Enterprise version of the spec. To generate the Enterprise version
of a client you would run `./bin/generate_client -l python --enterprise`.

## Manual Testing

You can access a compatible version of the the Conjur command line
interface by starting the `cli` docker compose container:
```shell
$ ./bin/cli
```

## Releasing

A new release must be created whenever a new version of [Conjur](https://github.com/cyberark/conjur)
is released that has updates to the REST API.

### Verify and update dependencies
1. Review the [NOTICES.txt](./NOTICES.txt) file and ensure it reflects the current
   set of dependencies in the [Gemfile](./Gemfile)
1. If a new dependency has been added, a dependency has been dropped, or a version
   has changed since the last tag - make sure the NOTICES file is up-to-date with
   the new versions

### Update the version and changelog
1. Examine the changelog and decide on the version bump rank (major, minor, patch).
1. Change the title of _Unreleased_ section of the changelog to the target
version.
   - Be sure to add the date (ISO 8601 format) to the section header.
1. Add a new, empty _Unreleased_ section to the changelog.
   - Remember to update the references at the bottom of the document.
1. Change `spec/openapi.yml` file's version object to reflect the change.
1. Commit these changes (including the changes to NOTICES.txt, if there are any).
   `Bump version to x.y.z` is an acceptable commit message.
1. Push your changes to a branch, and get the PR reviewed and merged.

### Tag the version
1. Tag the version on the master branch using eg. `git tag -s vx.y.z -m vx.y.z`. Note this
   requires you to be able to sign releases. Consult the
   [github documentation on signing commits](https://help.github.com/articles/signing-commits-with-gpg/)
   on how to set this up.

1. Push the tag: `git push vx.y.z` (or `git push origin vx.y.z` if you are working
   from your local machine).

### Add a new GitHub release

1. Create a new release from the tag in the GitHub UI
1. Add the [CHANGELOG](./CHANGELOG.txt) for the current version to the GitHub release description

### Enterprise Releases

We currently do not have official spec releases for Conjur Enterprise. Versions of the spec can be
generated using `./bin/transform --enterprise` which outputs a usable version of the spec to `out/enterprise/spec`.
