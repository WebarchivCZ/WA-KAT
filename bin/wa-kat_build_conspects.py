#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import bz2
import json
import os.path
import argparse

import marcxml_parser

from tqdm import tqdm


# Functions & classes =========================================================
def read_file(fn):
    with bz2.BZ2File(fn) as f:
        data = f.read().split("</record>")

    for chunk in tqdm(data, total=len(data)):
        yield chunk + "\n</record>\n"


def records_iterator(xml_records):
    for record in xml_records:
        if "<record" not in record:
            continue

        yield marcxml_parser.MARCXMLRecord(record)


def parse_conspectus(records):
    conspectus = {}

    conspects = []
    subconspects = []
    for record in records:
        if record.get("190k"):
            conspects.append(record)
        else:
            subconspects.append(record)

    for conspect in conspects:
        uid = conspect["190k"][0]
        name = conspect["190x"][0]

        if name.startswith("*"):
            name = name[1:]

        conspectus[uid] = {
            "id": uid,
            "name": name,
            "subconspects": {}
        }

    def parse_subconspect(record):
        uid = record["1909"][0]
        name = record["190x"][0]
        mdt = record["190a"][0]

        en_name = (record.get("790x") or [None])[0]
        ddc = (record.get("790a") or [None])[0]

        return uid, mdt, {
            "conspect_id": uid,
            "name": name,
            "mdt": mdt,
            "en_name": en_name,
            "ddc": ddc,
        }

    for subconspect in subconspects:
        uid, mdt, record = parse_subconspect(subconspect)

        conspectus[uid]["subconspects"][mdt] = record

    return conspectus


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
            This program may be used to convert Conspectus / Subconspectus set
            in MARC XML to JSON."""
    )
    parser.add_argument("XML_FILE", help="MARC XML file packed in .bz2.")
    args = parser.parse_args()

    if not os.path.exists(args.XML_FILE):
        sys.stderr.write("`%s` not found!\n" % args.XML_FILE)
        sys.exit(1)

    if not args.XML_FILE.endswith(".bz2"):
        sys.stderr.write("File is required to be XML packed in .bz2.")
        sys.exit(1)

    records = records_iterator(
        read_file(args.XML_FILE)
    )
    print json.dumps(
        parse_conspectus(records),
        indent=4,
        sort_keys=True,
    )
