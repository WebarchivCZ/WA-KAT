#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This file generates template with HTML / Brython application for the user.
"""
#
# Imports =====================================================================
import os
import json
import os.path

from bottle import get
from bottle import abort
from bottle import request
from bottle import template
from bottle import static_file

from shared import gzip_cache
from shared import read_template
from shared import in_template_path

from ..connectors import seeder


# Variables ===================================================================
INDEX_PATH = in_template_path("index_vertical.html")
STATIC_PATH = in_template_path("static")


# Functions & classes =========================================================
def read_index_template():
    """
    Open the template file and return it's content.

    Returns:
        str: Template content.
    """
    return read_template(INDEX_PATH)


def render_registered(url_id, remote_info):
    """
    Render template file for the registered user, which has some of the values
    prefilled.

    Args:
        url_id (str): Seeder URL id.
        remote_info (dict): Informations read from Seeder.

    Returns:
        str: Template filled with data.
    """
    return template(
        read_index_template(),
        registered=True,
        url=remote_info["url"],
        seeder_data=json.dumps(remote_info),
        url_id=url_id,
    )


def render_unregistered(error=None):
    """
    Render template file for the unregistered user.

    Args:
        error (str, default None): Optional error message.

    Returns:
        str: Template filled with data.
    """
    return template(
        read_index_template(),
        registered=False,
        error=error,
        seeder_data=None,
        url_id=None,
    )


# API =========================================================================
@get("/static/js/brython_dist.js")
def gzipped_brython():
    """
    Virtual file ``/static/js/brython_dist.js`` used as static GZIP cache to
    speed-up loading of `big` files.
    """
    path = os.path.join(STATIC_PATH, "js/brython_dist.js")
    return gzip_cache(path)


@get("/static/<fn:path>")
def static_data(fn):
    """
    Static file handler. This functions accesses all static files in ``static``
    directory.
    """
    file_path = os.path.normpath(fn)
    full_path = os.path.join(STATIC_PATH, file_path)

    if not os.path.exists(full_path):
        abort(404, "Soubor '%s' neexistuje!" % fn)

    return static_file(
        file_path,
        STATIC_PATH
    )


@get("/")
def render_form_template():
    """
    Rennder template for user.

    Decide whether the user is registered or not, pull remote info and so on.
    """
    error = ""
    remote_info = {}
    registered_user_id = request.query.get("url_id", False)

    # try to read remote info, the the url_id parameter was specified
    if registered_user_id:
        try:
            remote_info = seeder.get_remote_info(registered_user_id)
        except AssertionError:  #: TODO: requests error
            registered_user_id = False
            error = "Seeder neposlal očekávaná data.\n"

    if registered_user_id and remote_info:
        return render_registered(registered_user_id, remote_info)

    if not remote_info:
        error += "Seeder je nedostupný!\n"

    return render_unregistered(error)
