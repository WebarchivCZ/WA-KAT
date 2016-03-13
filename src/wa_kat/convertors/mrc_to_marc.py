#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import defaultdict

from marcxml_parser import MARCXMLRecord
from marcxml_parser.tools.resorted import resorted


# Functions & classes =========================================================
def mrc_to_marc(mrc):
    # ignore blank lines
    lines = [
        line
        for line in mrc.splitlines()
        if line.strip()
    ]

    def split_to_parts(lines):
        for line in lines:
            first_part, second_part = line.split(" L ", 1)

            yield line, first_part, second_part.lstrip()

    control_lines = []
    data_lines = []
    for line, first_part, second_part in split_to_parts(lines):
        if second_part.startswith("$"):
            data_lines.append(line)
        else:
            control_lines.append(line)

    # convert controlfield lines
    record = MARCXMLRecord()
    record.oai_marc = True
    for line, descr, content in split_to_parts(control_lines):
        record.controlfields[descr.strip()[:3]] = content

    def get_subfield_dict(line):
        fields = (
            (field[0], field[1:])
            for field in line.split("$$")[1:]
        )

        fields_dict = defaultdict(list)
        for key, val in fields:
            fields_dict[key].append(val)

        return fields_dict

    # convert datafield lines
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


def dict_to_mrc(code, dicts):
    def _dict_to_mrc(code, d):
        i1 = d.get("i1", d.get("ind1"))
        i2 = d.get("i2", d.get("ind2"))

        one_chars = [k for k in d.keys() if len(k) == 1]
        out = "%s%s%s L " % (code, i1, i2)
        for key in resorted(one_chars):
            for item in d[key]:
                out += "$$%s%s" % (key, item)

        return out

    return [
        _dict_to_mrc(code, d)
        for d in dicts
    ]
