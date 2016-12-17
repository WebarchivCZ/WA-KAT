#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
REST API definitions.
"""
#
# Imports =====================================================================
from os.path import join
from StringIO import StringIO

from bottle import post
from bottle import response
from bottle import HTTPError
from bottle_rest import form_to_params

from ..settings import API_PATH


# REST API modules
import db
import aleph_api
import virtual_fs
import bottle_index
import analyzers_api
from to_output import to_output
from keywords import get_kw_list


# REST API ====================================================================
@post(join(API_PATH, "as_file/<fn:path>"))
@form_to_params
def download_as_file(fn, data=None):
    """
    Download given `data` as file `fn`. This service exists to allow frontend
    present user with downloadable files.
    """
    if data is None:
        raise HTTPError(500, "This service require POST `data` parameter.")

    response.set_header("Content-Type", "application/octet-stream")
    response.set_header(
        "Content-Disposition",
        'attachment; filename="%s"' % fn
    )

    return StringIO(data)
