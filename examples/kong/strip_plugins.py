import yaml

with open("out/kong/kong.yml", "r") as f:
    kong_yaml = yaml.full_load(f)

routes = kong_yaml["services"][0]["routes"]
for route in routes:
    if "plugins" in route:
        route.pop("plugins")

with open("out/kong/kong.yml", "w") as f:
    dump = yaml.dump(kong_yaml, default_flow_style=False)
    f.write(dump)