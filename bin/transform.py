#!/usr/bin/env python

import sys
import pathlib
import os

import yaml

class Annotation:
    """Defines an object annotation in the spec

    Defined as all fields under x-conjur-settings.
    e.g. to annotate the object Path:

    .. code-block:: yaml

        Path:
            x-conjur-settings:
                enterprise-only: true
    """
    def __init__(self, annotation: dict, obj_path: list):
        annotation = annotation['x-conjur-settings']
        self.annotation = annotation
        self.obj_path = obj_path
        if 'enterprise-only' in annotation and isinstance(annotation['enterprise-only'], bool):
            self.dap_only = annotation['enterprise-only']
        else:
            self.dap_only = False

def __find_annotations(obj, object_path=None):
    """Helper function recurses through a yaml object and returns a list of all annotations"""
    annotations = []
    if not isinstance(obj, dict):
        return annotations
    for i in obj:
        if i == 'x-conjur-settings':
            annotations.append(Annotation({i: obj[i]}, object_path))
        annotations += __find_annotations(obj[i], object_path + [i])
    return annotations

def find_annotations(obj):
    """Finds all annotations in a given object"""
    return __find_annotations(obj, [])

def verify_object_exists(obj: dict, obj_path: list):
    """Verifies that a given object has a given sub-object defined by obj_path"""
    if not obj_path:
        return True
    if obj_path[0] in obj:
        return verify_object_exists(obj[obj_path[0]], obj_path[1:])
    return False

def remove_object(obj, obj_path):
    """Removes the sub-object defined by obj_path from obj"""
    if len(obj_path) == 1:
        del obj[obj_path[0]]
    else:
        remove_object(obj[obj_path[0]], obj_path[1:])
        if obj[obj_path[0]] == {}:
            del obj[obj_path[0]]

def usage():
    """Prints usage information and exits"""
    print("Usage: transform <input-file> [--enterprise/--oss]")
    sys.exit()

def get_output_dir(generate_dap):
    """Finds which directory to output to, this is dependant on whether we
    are generating the enterprise or oss version of the spec"""
    if generate_dap:
        output_dir = pathlib.Path('./out/enterprise/spec')
    else:
        output_dir = pathlib.Path('./out/oss/spec')
    if not output_dir.exists():
        output_dir.mkdir()
    return output_dir

if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()

    input_file = pathlib.Path(sys.argv[1])
    if '--enterprise' in sys.argv:
        generate_dap = True
    elif '--oss' in sys.argv:
        generate_dap = False
    else:
        usage()

    # read in the input object we are parsing
    with input_file.open(encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
            sys.exit(1)

    # retrieve a list of annotations in the object we are parsing
    annotations = find_annotations(data)

    # For each found annotation check if we need to remove it then do so
    for i in annotations:
        if i.dap_only and not generate_dap and verify_object_exists(data, i.obj_path):
            remove_object(data, i.obj_path)

    # write the output file
    output_dir = get_output_dir(generate_dap)
    with (output_dir / os.path.basename(input_file.name)).open(mode="w", encoding="utf-8") as f:
        f.write(yaml.dump(data))
