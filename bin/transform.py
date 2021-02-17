#!/usr/bin/env python3

import sys
import pathlib
import os

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

def usage():
    print("Usage: transform <input-file> [--dap/--conjur]")
    exit()

def get_output_dir(generate_dap):
    if generate_dap:
        output_dir = pathlib.Path('./out/dap/spec')
    else:
        output_dir = pathlib.Path('./out/conjur/spec')
    if not output_dir.exists():
        output_dir.mkdir()
    return output_dir

if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()

    input_file = pathlib.Path(sys.argv[1])
    if '--dap' in sys.argv:
        generate_dap = True
    elif '--oss' in sys.argv:
        generate_dap = False
    else:
        usage()

    with input_file.open() as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
            exit(1)

    annotations = find_annotations(data, [])
    for i in annotations:
        if i.dap_only and not generate_dap and verify_object_exists(data, i.obj_path):
            remove_object(data, i.obj_path)

    output_dir = get_output_dir(generate_dap)
    with (output_dir / input_file.name).open(mode="w") as f:
        f.write(yaml.dump(data))
