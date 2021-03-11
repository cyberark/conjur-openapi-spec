# OpenAPI Spec Integration Testing

## Python

The Python integration tests are written for version >=3.8 and run against
the `conjur:edge` image. The tests are built on top of the [unittest](https://docs.python.org/3/library/unittest.html)
framework.

On the surface level the framework works by running each subclass of `unittest.TestCase` that it
finds. Before any of the tests are run the `setUpClass` method is run, and before each individual
test is run the `setUp` method is run. The same is true for `tearDownClass` and `tearDown`.

Each of the test classes inherits from the `api_config.ConfiguredTest` class which itself inherts from
`unittest.TestCase`. The `ConfiguredTest` class includes `setUpClass` and `tearDownClass` methods which
make sure each test class has an already authenticated client and a badly authenticated client for
failing tests.

## C#/.NET

The C# tests are built on top of the [Xunit](https://xunit.net/) framework.

Instead of being a full project setup the C# tests are just a set of files which
are copied into the generated clients testing directory. The tests are then run by
changing into the generated clients project directory and executing `dotnet test`.
