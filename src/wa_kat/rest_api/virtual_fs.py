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


def in_second_virtual_path(fn):
    """
    Brython has problem with .. imports, so I have to insert the submodule
    into the components path manually.
    """
    return join("/static/js/Lib/site-packages/components/virtual_fs", fn)


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
@get(in_second_virtual_path("__init__.py"))
@python_mime
def init_api():
    return PY_HEADER


@get(in_virtual_path("settings.py"))
@get(in_second_virtual_path("settings.py"))
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
@get(in_second_virtual_path("conspectus.py"))
@python_mime
@lru_cache()
def conspectus_api():
    conspectus_dict = json.loads(read_template("full_conspectus.json"))

    # raw conspectus dictionary
    out = PY_HEADER + "consp_dict = %s\n\n" % repr(conspectus_dict)

    # (consp, id) pairs
    cosp_id_pairs = sorted(
        (x["name"], x["id"])
        for x in conspectus_dict.values()
    )
    out += "cosp_id_pairs = %s\n\n" % repr(cosp_id_pairs)

    # mdt -> subconspect mapping
    subs_by_mdt = [
        x["subconspects"].values()
        for x in conspectus_dict.values()
    ]
    subs_by_mdt = {d["mdt"]: d for d in sum(subs_by_mdt, [])}
    out += "subs_by_mdt = %s\n\n" % repr(subs_by_mdt)

    # subconspect_name -> subconspect mapping
    out += "mdt_by_name = %s\n\n" % repr({
        d["name"]: d["mdt"]
        for d in subs_by_mdt.values()
    })

    return out


@get(in_virtual_path("periodes.py"))
@get(in_second_virtual_path("periodes.py"))
@python_mime
@lru_cache()
def periode_api():
    periodes = read_template("periode.txt").decode("utf-8")

    return PY_HEADER + "periode_list = %s\n\n" % repr(periodes.splitlines())
