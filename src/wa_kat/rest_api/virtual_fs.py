#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This file provides virtual fileystem for Brython files, so some of the values
may be transported to the frontend from backend as pre-parsed python data.
"""
# Imports =====================================================================
import json
from os.path import join

from bottle import get
from bottle import response
from backports.functools_lru_cache import lru_cache

from .. import settings

from shared import read_template


# Variables ===================================================================
PY_HEADER = """#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
"""


# Functions & classes =========================================================
def in_virtual_path(fn):
    return join("/static/js/Lib/site-packages/virtual_fs", fn)


def python_mime(fn):
    """
    Add correct MIME type to the decorated function.
    """
    def python_mime_decorator(*args, **kwargs):
        response.content_type = "text/x-python"

        return fn(*args, **kwargs)

    return python_mime_decorator


# API =========================================================================
@get(in_virtual_path("__init__.py"))
@python_mime
def init_api():
    return PY_HEADER


@get(in_virtual_path("settings.py"))
@python_mime
@lru_cache()
def settings_api():
    variables = [
        "%s = %s" % (var, repr(getattr(settings, var)))
        for var in sorted(dir(settings))
        if not var.startswith("_") and var.upper() == var
    ]

    return PY_HEADER + "\n\n".join(variables)


@get(in_virtual_path("conspectus.py"))
@python_mime
@lru_cache()
def conspectus_api():
    conspectus_dict = json.loads(read_template("full_conspectus.json"))

    return PY_HEADER + "consp_dict = %s\n" % repr(conspectus_dict)
