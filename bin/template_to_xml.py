#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import os.path
import argparse
from collections import defaultdict

from marcxml_parser import MARCXMLRecord


# Functions & classes =========================================================
def convert_template(data):
    # ignore blank lines
    lines = [
        line
        for line in data.splitlines()
        if line.strip()
    ]

    def split_to_parts(lines):
        for line in lines:
            first_part, second_part = line.split(" L ", 1)

            yield line, first_part, second_part.lstrip()

    # get list of control and data lines
    control_lines = [
        line
        for line, first_part, second_part in split_to_parts(lines)
        if not second_part.startswith("$")
    ]

    data_lines = [
        line
        for line, first_part, second_part in split_to_parts(lines)
        if second_part.startswith("$")
    ]

    # convert control lines
    record = MARCXMLRecord()
    record.oai_marc = True
    for line, descr, content in split_to_parts(control_lines):
        record.controlfields[descr.strip()] = content

    def get_subfield_dict(line):
        fields = (
            (field[0], field[1:])
            for field in line.split("$$")[1:]
        )

        fields_dict = defaultdict(list)
        for key, val in fields:
            fields_dict[key].append(val)

        return fields_dict

    # convert data lines
    for line, descr, content_line in split_to_parts(data_lines):
        name = descr[:3]
        i1 = descr[3]
        i2 = descr[4]

        record.add_data_field(
            name,
            i1,
            i2,
            get_subfield_dict(content_line)
        )

    return record.to_XML()


def convert_file(fn):
    if not os.path.exists(fn):
        sys.stderr.write("Can't open `%s`!\n" % fn)
        sys.exit(1)

    with open(fn) as f:
        data = f.read()

    return convert_template(data)


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "INPUT",
        nargs=1,
        help="Input file."
    )

    args = parser.parse_args()

    print convert_file(args.INPUT[0])
