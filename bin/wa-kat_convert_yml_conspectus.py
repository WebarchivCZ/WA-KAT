#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import json
import argparse

import yaml


# Functions & classes =========================================================
def load_yaml_file(path):
    with open(path) as f:
        return yaml.load(f)


def to_json(data):
    return json.dumps(
        data,
        indent=4,
        separators=(',', ': ')
    )


def convert_to_dict_list(data):
    categories = {
        item["id"]: {
            "id": item["id"],
            "name": item["category"],
            "sub_categories": [],
        }
        for item in data
        if "category" in item
    }

    # map sub-conspects
    for item in data:
        if "category" in item:
            continue

        sub_obj = {
            "id": item["id"],
            "name": item["subcategory"],
            "subcategory_id": str(item["subcategory_id"]).replace(",", "."),
        }

        categories[item["conspectus_id"]]["sub_categories"].append(sub_obj)

    return sorted(
        categories.values(),
        key=lambda x: x["id"]
    )


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
            This script is used to convert conspectus YAML database dump into
            internal file format used by WA-KAT and Seeder.
        """
    )
    parser.add_argument(
        "FILE",
        nargs=1,
        help="Name of the input YAML file."
    )
    args = parser.parse_args()

    data = load_yaml_file(args.FILE[0])

    print to_json(convert_to_dict_list(data))
