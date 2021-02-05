import yaml

class Annotation:
    def __init__(self, annotation: dict, obj_path: list):
        annotation = annotation['x-conjur-settings']
        self.annotation = annotation
        self.obj_path = obj_path
        if 'dap-only' in annotation and isinstance(annotation['dap-only'], bool):
            self.dap_only = annotation['dap-only']
        else:
            self.dap_only = False

def find_annotations(obj, object_path=[]):
    annotations = list()
    if not isinstance(obj, dict):
        return annotations
    for i in obj:
        if i == 'x-conjur-settings':
            annotations.append(Annotation({i: obj[i]}, object_path))
        new_annotations = find_annotations(obj[i], object_path + [i])
        if new_annotations:
            annotations += new_annotations
    return annotations

def verify_object_exists(obj: dict, obj_path: list):
    if not obj_path:
        return True
    if obj_path[0] in obj:
        return verify_object_exists(obj[obj_path[0]], obj_path[1:])
    else:
        return False

def remove_object(data, obj_path):
    if len(obj_path) == 1:
        del data[obj_path[0]]
    else:
        remove_object(data[obj_path[0]], obj_path[1:])
        if data[obj_path[0]] == {}:
            del data[obj_path[0]]

with open("spec.yml", "r") as f:
    try:
        data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(e)
        exit(1)

annotations = find_annotations(data, [])
for i in annotations:
    if i.dap_only and verify_object_exists(data, i.obj_path):
        remove_object(data, i.obj_path)

with open("out.yml", "w") as f:
    f.write(yaml.dump(data))
