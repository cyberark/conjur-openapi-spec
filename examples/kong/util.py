import yaml
import sys

def bump_spec_version():
    """Converts conjurKubernetesMutualTls to OAI v3.1 compatible definition.
    OAI v3.1 is not supported by spec bundling tool"""
    with open("spec.yml", "r") as f:
        spec_yaml = yaml.full_load(f)

    security_schemes = spec_yaml["components"]["securitySchemes"]
    security_schemes["conjurKubernetesMutualTls"]["type"] = "mutualTLS"
    security_schemes["conjurKubernetesMutualTls"].pop("scheme")

    with open("tmp_spec.yml", "w") as f:
        dump = yaml.dump(spec_yaml, default_flow_style=False)
        f.write(dump)

def strip_plugins():
    """Removes Kong authentication plugins from each route,
    allow Conjur to handle authentication headers"""
    with open("out/kong/kong.yml", "r") as f:
        kong_yaml = yaml.full_load(f)

    routes = kong_yaml["services"][0]["routes"]
    for route in routes:
        if "plugins" in route:
            route.pop("plugins")

    with open("out/kong/kong.yml", "w") as f:
        dump = yaml.dump(kong_yaml, default_flow_style=False)
        f.write(dump)

if __name__ == '__main__':
    globals()[sys.argv[1]]()
