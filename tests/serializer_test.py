#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __future__ import unicode_literals

import json
import requests


# Variables ===================================================================
data = {
    'author': 'nějaký autor',
    'periodicity': 'periodicita',
    'conspect': "821.17",
    'creation_date': '1212121',
    'frequency': None,
    'keywords': [
        'HTML',
        'k\xfd\u010d',
        'st\xe1\u0159\xed',
        'C++',
        '\u0159\xe1d'
    ],
    'annotation': 'Popis str\xe1nek.\n\nDescription of the web.',
    'language': 'nějaký jazyk',
    'title': 'nějaký titulek',
    'url': 'http://vps4life.kitakitsune.org/example.html',
    'issn': '1805-8787',
    'place': 'nějaké místo'
}


# Functions & classes =========================================================



# Main program ================================================================
if __name__ == '__main__':
    resp = requests.post(
        "http://localhost:8080/api_v1/to_marc",
        data={"data": json.dumps(data)}
    )

    print resp.text
