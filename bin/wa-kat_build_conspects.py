#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import bz2

import dhtmlparser
import marcxml_parser

from tqdm import tqdm


# Variables ===================================================================
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


def create_conspectus(records):
    conspectus = {}

    for record in records:
        pass


# Main program ================================================================
if __name__ == '__main__':
    fn = "../../balkons1.xml.bz2"
    print len(list(records_iterator(read_file(fn))))
