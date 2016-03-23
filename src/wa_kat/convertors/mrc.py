#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module offers functions for working with MRC format used in Aleph's
desktop client.
"""
#
# Imports =====================================================================
from collections import defaultdict

from marcxml_parser import MARCXMLRecord
from marcxml_parser.tools.resorted import resorted


# Functions & classes =========================================================
def mrc_to_marc(mrc):
    """
    Convert MRC data format to MARC XML.

    Args:
        mrc (str): MRC as string.

    Returns:
        str: XML with MARC.
    """
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


def dicts_to_mrc(code, dicts):
    """
    Convert `dicts` under `code` to MRC. This is used to compose some of the
    data from user's input to MRC template, which is then converted to
    MARC XML / Dublin core.

    Args:
        code (str): Code of the aleph field, whic hshould be used.
        dicts (dict): Dict with aleph fields (i1/i2, a..z, 0..9) and
            informations in this fields.

    Returns:
        list: List of lines with MRC data.
    """
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


def val_to_mrc(code, val):
    """
    Convert one single `val` to MRC.

    This function may be used for control fields in MARC records.

    Args:,
        code (str): Code of the field.
        val (str): Value of the field.

    Returns:
        str: Correctly padded MRC line with field.
    """
    code = str(code)
    if len(code) < 3:
        code += (3 - len(code)) * " "

    return "%s   L %s" % (code, val)


def item_to_mrc(code, val):
    """
    Convert `val` to MRC, whether it is dict or string.

    Args:
        code (str): Code of the field.
        val (str or dict): Value of the field.

    Returns:
        list: MRC lines for output template.
    """
    if isinstance(val, basestring):
        return [val_to_mrc(code, val)]

    if isinstance(val, dict):
        val = [val]

    return dicts_to_mrc(code, val)
