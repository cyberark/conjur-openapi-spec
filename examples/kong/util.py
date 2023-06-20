import yaml
import sys
from typing import Any

def read_yaml(path: str) -> Any:
    with open(path, "r") as f:
        content = yaml.safe_load(f)
    return content

def write_yaml(path: str, content: str) -> None:
    with open(path, "w") as f:
        dump = yaml.safe_dump(content, default_flow_style=False)
        f.write(dump)

def bump_spec_version():
    """Converts conjurKubernetesMutualTls to OAI v3.1 compatible definition.
    OAI v3.1 is not supported by spec bundling tool"""
    spec_yaml = read_yaml("spec.yml")

    security_schemes = spec_yaml["components"]["securitySchemes"]
    security_schemes["conjurKubernetesMutualTls"]["type"] = "mutualTLS"
    security_schemes["conjurKubernetesMutualTls"].pop("scheme")

    write_yaml("tmp_spec.yml", spec_yaml)

def strip_plugins():
    """Removes Kong authentication plugins from each route,
    allow Conjur to handle authentication headers"""
    kong_yaml = read_yaml("out/kong/kong.yml")

    del kong_yaml["services"][0]["plugins"]

    routes = kong_yaml["services"][0]["routes"]
    for route in routes:
        if "plugins" in route:
            route.pop("plugins")

    write_yaml("out/kong/kong.yml", kong_yaml)

def update_server_url():
    """A Kong declarative configuration requires a defined target server. Using
    http://conjur:80 allows a containers Kong Gateway to target a
    local Conjur instance."""
    spec_yaml = read_yaml("tmp_spec.yml")

    spec_yaml["servers"][0]["url"] = "http://conjur:80"

    write_yaml("tmp_spec.yml", spec_yaml)

if __name__ == '__main__':
    globals()[sys.argv[1]]()
