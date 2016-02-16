#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from os.path import join

from bottle import post
from bottle_rest import form_to_params

from ..connectors import aleph

from shared import API_PATH


# Variables ===================================================================
API_PATH = join(API_PATH, "aleph")


# Functions & classes =========================================================
@post(join(API_PATH, "records_by_issn"))
@form_to_params
def records_by_issn(issn):
    return [
        result.get_mapping()
        for result in aleph.by_issn(issn)
    ]


@post(join(API_PATH, "authors_by_name"))
@form_to_params
def authors_by_name(name):
    return [
        author._asdict()
        for author in aleph.Author.search_by_name(name)
    ]
