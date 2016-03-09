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
from os.path import join

from bottle import get
from bottle import response

from shared import in_template_path


# Variables ===================================================================
# Functions & classes =========================================================
def in_virtual_path(fn):
    return join("/static/js/Lib/site-packages/virtual_fs", fn)


def python_mime(fn):
    def python_mime_decorator(*args, **kwargs):
        response.content_type = "text/x-python"

        return fn(*args, **kwargs)

    return python_mime_decorator


# API =========================================================================
@get(in_virtual_path("__init__.py"))
@python_mime
def init():
    return """#! /usr/bin/env python
# -*- coding: utf-8 -*-
    """
