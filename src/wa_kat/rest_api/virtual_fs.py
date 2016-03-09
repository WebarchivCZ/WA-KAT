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

from .. import settings

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
def init_api():
    return """#! /usr/bin/env python
# -*- coding: utf-8 -*-
    """


@get(in_virtual_path("settings.py"))
@python_mime
def settings_api():
    out = "\n"

    for var in sorted(dir(settings)):
        if var.startswith("_") or var.upper() != var:
            continue

        out += "%s = %s\n\n" % (var, repr(getattr(settings, var)))

    return """#! /usr/bin/env python
# -*- coding: utf-8 -*-
#""" + out


# http://localhost:8080/static/js/Lib/site-packages/virtual_fs/__init__.py
@get(in_virtual_path("conspectus.py"))
@python_mime
def conspectus_api():
    return """#! /usr/bin/env python
# -*- coding: utf-8 -*-
    """
