#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import os.path

import requests
from bottle import get
from bottle import abort
from bottle import request
from bottle import template
from bottle import static_file

from . import settings


# Variables ===================================================================
TEMPLATE_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "templates"
)
INDEX_PATH = os.path.join(TEMPLATE_PATH, "index_vertical.html")
STATIC_PATH = os.path.join(TEMPLATE_PATH, "static")


# Functions & classes =========================================================
def _read_template():
    with open(INDEX_PATH) as f:
        return f.read()


def render_registered(remote_info):
    return template(
        _read_template(),
        registered=True,
        url=remote_info["url"]
    )


def render_unregistered(error=None):
    return template(
        _read_template(),
        registered=False,
        error=error
    )


def get_remote_info(url_id):  # TODO: Add timeout, print error in case of exception
    resp = requests.get(settings.REMOTE_INFO_URL)
    resp.raise_for_status()
    data = resp.json()

    assert "url" in data

    return data


# TODO: REMOVE
@get("/" + settings.REMOTE_INFO_URL.split("/")[-1])
def mock_data():
    return {
        "url": "http://seznam.cz",
    }
# TODO: REMOVE


@get("/<fn:path>")
def static_data(fn):
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
    error = ""
    remote_info = {}
    registered_user_id = request.query.get("url_id", False)

    # try to read remote info, the the url_id parameter was specified
    if registered_user_id:
        try:
            remote_info = get_remote_info(registered_user_id)
        except AssertionError:
            registered_user_id = False
            error = "Server neposlal očekávaná data."

    if registered_user_id:
        return render_registered(remote_info)

    return render_unregistered(error)
