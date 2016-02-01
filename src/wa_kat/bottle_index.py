#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import json
import os.path

import requests
from bottle import get
from bottle import abort
from bottle import request
from bottle import template
from bottle import static_file

import settings
from zeo import ConspectDatabase
from rest_api.shared import gzip_cache
from rest_api.shared import read_template
from rest_api.shared import in_template_path


# Variables ===================================================================
INDEX_PATH = in_template_path("index_vertical.html")
STATIC_PATH = in_template_path("static")


# Functions & classes =========================================================
def _index_template():
    return read_template(INDEX_PATH)


def render_registered(remote_info):
    return template(
        _index_template(),
        registered=True,
        url=remote_info["url"],
        conspect=json.dumps(ConspectDatabase().data),
        periode=read_template("periode.txt"),
        GUI_TO_REST_PERIODE=settings.GUI_TO_REST_PERIODE,
    )


def render_unregistered(error=None):
    return template(
        _index_template(),
        registered=False,
        error=error,
        conspect=json.dumps(ConspectDatabase().data),
        periode=read_template("periode.txt"),
        GUI_TO_REST_PERIODE=settings.GUI_TO_REST_PERIODE,
    )


def get_remote_info(url_id):  # TODO: Add timeout, print error in case of exception
    resp = requests.get(settings.REMOTE_INFO_URL)
    resp.raise_for_status()
    data = resp.json()

    assert "url" in data

    return data


# API =========================================================================
# TODO: REMOVE
@get("/" + settings.REMOTE_INFO_URL.split("/")[-1])
def mock_data():
    return {
        "url": "http://seznam.cz",
    }
# TODO: REMOVE


@get("/static/js/brython_dist.js")
def gzipped_brython():
    """
    Static cache to speed-up loading of `big` files.
    """
    path = os.path.join(STATIC_PATH, "js/brython_dist.js")
    return gzip_cache(path)


@get("/static/<fn:path>")
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
        except AssertionError:  #: TODO: requests error
            registered_user_id = False
            error = "Server neposlal očekávaná data."

    if registered_user_id:
        return render_registered(remote_info)

    return render_unregistered(error)
