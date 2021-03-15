# Using the OpenAPI Spec with Kong OSS Gateway

Contrary to most API gateway services, Kong OSS does not provide a built-in tool for generating
a custom gateway given an OpenAPI spec. The script in this directory serves as an example for
setting up a Kong OSS gateway from an OpenAPI specification.

This example will stand up a Conjur server, as well as a Kong OSS Gateway Docker container.
Requests are processed by Kong before being routed to Conjur. This example does not implement
any of Kong's many plugins, including authentication, traffic control and analytics. More info on
Kong plugins can be found at Kong's [Plugin Hub](https://docs.konghq.com/hub/).

Converting an OpenAPI description to a Kong configuration requires
[Inso](https://github.com/Kong/insomnia/tree/develop/packages/insomnia-inso), a CLI for Kong's API
development tool [Insomnia](https://github.com/Kong/insomnia).

You can use Inso to generate a declarative Kong configuration from a bundled version of the
OpenAPI spec. Inso requires that the spec defines a server URL for Kong to target.

```bash
bin/bundle_spec

echo "servers:
  - url: http://host.docker.internal:80" >> spec.yml

docker run --rm -it \
  -v /path/to/openapi/project:/opt/openapi \
  node: latest \
  bash -c "
    npm i -g insomnia-inso \
    && cd /opt/openapi \
    && inso --verbose \
      generate config spec.yml \
      --type declarative \
      --output out/kong/kong.yml
  "
```

The above commands will generate a Kong configuration, but when it processes security schemes
defined in the OpenAPI spec, it includes Kong authentication plugins on each route. This causes
Kong to consume authentication credentials instead of passing them to Conjur. A Python
[script](strip_plugins.py) is included to remove these plugins, allowing Conjur to receive
credentials with each request.

```bash
docker run --rm \
  -v $(pwd):/opt/openapi \
  python:latest /bin/bash -c "
    cd /opt/openapi && \\
    pip3 install pyyaml && \\
    python3 examples/kong/strip_plugins.py
  "
```

After starting Kong OSS, HTTP request made to Conjur endpoints through Kong at
`http://localhost:8000` will be processed by Kong before being redirected to Conjur.
