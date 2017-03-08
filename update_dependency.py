#!/usr/bin/env python

import os
import sys
import yaml
import pprint

def usage():
    print("usage: update_dependency.py <filename> <meta|galaxy> <role_name> <role_version>")
    exit(1)

def parse_argv(argv):
    if len(argv) != 5:
        usage()

    filename = sys.argv[1]
    filetype = sys.argv[2]
    role_name = sys.argv[3]
    role_version = sys.argv[4]

    if filetype != "meta" and filetype != "galaxy":
        usage()

    return filename, filetype, role_name, role_version

def read_yml(filename):
    try:
        with open(filename, 'r') as stream:
            yml_data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print("Error occured while parsing input YML file {}".format(filename))
        exit(1)
    except IOError as exc:
        print("IO error occured while reading input YML file {}".format(filename))
        exit(1)

    return yml_data

def write_yml(filename, yml_data):
    try:
        with open(filename, 'w') as outfile:
            yaml.dump(yml_data, outfile, default_flow_style=False)
    except IOError as exc:
        print("IO error occured while writing YML file {}".format(filename))
        exit(1)

def update_dep(deps, role_name, role_version):
    new_deps = []
    deps_updated = False
    old_value = ""

    for dep in deps:
        depname = dep.get("name", False)
        depver = dep.get("version", False)

        if depname == role_name:
            old_value = depver
            if depver != role_version:
                deps_updated = True
                dep.update({"version": role_version})
        new_deps.append(dep)

    return new_deps, deps_updated, old_value

def main():

    # Parse arguments
    filename, filetype, role_name, role_version = parse_argv(sys.argv)

    # Get current directory path
    cwd = os.path.dirname(os.path.abspath(__file__))

    # root = os.path.abspath(os.path.join(cwd, "../../"))
    # meta_file = os.path.abspath(os.path.join(root, "meta/main.yml"))

    # Read YML data
    yml_data = read_yml(filename)

    # Parse YML data
    if filetype == "meta":
        if not isinstance(yml_data, dict):
            print("{} is wrong format.".format(filename))
            exit(1)
        dependencies = yml_data.get("dependencies", False)
        if not dependencies:
            print("{} is missing dependency section.".format(filename))
            exit(1)
    else:
        dependencies = yml_data

    # Update dependency list with desired role version
    new_dependencies, deps_updated, old_value = update_dep(dependencies, role_name, role_version)

    # Inform if no change needed and fail if role is not found
    if not deps_updated and old_value == role_version:
        print("Role {} is already at version {}.".format(role_name, role_version))
        exit(0)
    elif not deps_updated and old_value == "":
        print("Role {} is not found.".format(role_name, role_version))
        exit(1)

    # Prepare output YML
    if filetype == "meta":
        yml_data.update({"dependencies": new_dependencies})
    else:
        yml_data = new_dependencies

    # Write resulting file
    write_yml(filename, yml_data)

    print "Updated role {} to {} in {}".format(role_name,role_version, filename)

if __name__ == '__main__':
  main()
