#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
REST API provider for the Aleph system.
"""
#
# Imports =====================================================================
from os.path import join

from bottle import post
from bottle_rest import form_to_params

from ..connectors import aleph
from ..settings import API_PATH


# Variables ===================================================================
API_PATH = join(API_PATH, "aleph")


# Functions & classes =========================================================
@post(join(API_PATH, "records_by_issn"))
@form_to_params
def records_by_issn(issn):
    """
    Search NTK Aleph ISSN base for given `issn`.

    Returns:
        list: List of ISSN records.
    """
    return [
        result.get_mapping()
        for result in aleph.by_issn(issn)
    ]


@post(join(API_PATH, "authors_by_name"))
@form_to_params
def authors_by_name(name):
    """
    Search NK Aleph authority base for authors matching the `name`.

    Returns:
        list: List of matching authors.
    """
    return [
        author._asdict()
        for author in aleph.Author.search_by_name(name)
    ]
