#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This file provides virtual fileystem for Brython files, so some of the values
may be transported to the frontend from backend as pre-parsed python data.
"""
#
# Imports =====================================================================
import json
from os.path import join
from functools import wraps

from bottle import get
from bottle import response
from backports.functools_lru_cache import lru_cache

from .. import settings

from shared import read_template


# Variables ===================================================================
#: This is used as header of all virtual .py files
PY_HEADER = """#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
"""


# Functions & classes =========================================================
def in_virtual_path(fn):
    """
    Return `fn` in absolute path to root of the brython files.

    Args:
        fn (str): Name of the file which should be put into abs path.

    Returns:
        str: Absolute path of the file.
    """
    return join("/static/js/Lib/site-packages/virtual_fs", fn)


def in_second_virtual_path(fn):
    """
    Brython has problem with .. imports, so I have to insert the `submodule`
    package into the root path manually.

    Args:
        fn (str): Name of the file which should be put into abs path.

    Returns:
        str: Absolute path of the file in `components` submodule.
    """
    return join("/static/js/Lib/site-packages/components/virtual_fs", fn)


def python_mime(fn):
    """
    Decorator, which adds correct MIME type for python source to the decorated
    bottle API function.
    """
    @wraps(fn)
    def python_mime_decorator(*args, **kwargs):
        response.content_type = "text/x-python"

        return fn(*args, **kwargs)

    return python_mime_decorator


# API =========================================================================
@get(in_virtual_path("__init__.py"))
@get(in_second_virtual_path("__init__.py"))
@python_mime
def init_api():
    """
    Virtual ``__init__.py`` file for the whole ``virtual_fs/`` directory.
    """
    return PY_HEADER


@get(in_virtual_path("settings.py"))
@get(in_second_virtual_path("settings.py"))
@python_mime
@lru_cache()
def settings_api():
    """
    Virtual ``settings.py`` with values transported from real
    :mod:`settings.py`, so the Brython frontend may be configured same way as
    backend.

    Some of the critical values are intentionally left out.
    """
    variables = [
        "%s = %s" % (var, repr(getattr(settings, var)))
        for var in sorted(dir(settings))
        if (not var.startswith("_") and var.upper() == var and
            not var.startswith("SEEDER"))  # hide the private tokens and url
    ]

    return PY_HEADER + "\n\n".join(variables)


@get(in_virtual_path("conspectus.py"))
@get(in_second_virtual_path("conspectus.py"))
@python_mime
@lru_cache()
def conspectus_api():
    """
    Virtual ``conspectus.py`` file for brython. This file contains following
    variables:

    Attributes:
        consp_dict (dict): Dictionary with conspects.
        cosp_id_pairs (list): List of tuples ``(name, id)`` for conspectus.
        subs_by_mdt (dict): Dictionary containing ``mdt: sub_dict``.
        mdt_by_name (dict): ``name: mdt`` mapping.

    Note:
        Example of the `cons_dict` format::

            {
                "1": {
                    "id": "1",
                    "name": "Antropologie, etnografie",
                    "subconspects": {
                        "304": {
                            "conspect_id": "1",
                            "name": "Kulturn\u00ed politika"
                            "en_name": "Culture and institutions",
                            "mdt": "304",
                            "ddc": "306.2",
                        },
                        ...
                    }
                },
                ...
            }

    Values are stored in json and upacked after load. This is used because of
    performance issues with parsing large brython files.
    """
    def to_json(data):
        """
        JSON conversion is used, because brython has BIG performance issues
        when parsing large python sources. It is actually cheaper to just load
        it as JSON objects.

        Load times:
            Brython: 24s firefox, 54s chromium
            JSON: 14s firefox, 9s chromium
        """
        return repr(json.dumps(data))

    conspectus_dict = json.loads(read_template("full_conspectus.json"))

    # raw conspectus dictionary
    out = PY_HEADER
    out += "import json\n"

    out += "consp_dict = json.loads(%s)\n\n" % to_json(conspectus_dict)

    # (consp, id) pairs
    cosp_id_pairs = sorted(
        (x["name"], x["id"])
        for x in conspectus_dict.values()
    )
    out += "cosp_id_pairs = json.loads(%s)\n\n" % to_json(cosp_id_pairs)

    # mdt -> subconspect mapping
    subs_by_mdt = [
        x["subconspects"].values()
        for x in conspectus_dict.values()
    ]
    subs_by_mdt = {d["mdt"]: d for d in sum(subs_by_mdt, [])}
    out += "subs_by_mdt = json.loads(%s)\n\n" % to_json(subs_by_mdt)

    # subconspect_name -> subconspect mapping
    out += "mdt_by_name = json.loads(%s)\n\n" % to_json({
        d["name"]: d["mdt"]
        for d in subs_by_mdt.values()
    })

    return out


@get(in_virtual_path("periodes.py"))
@get(in_second_virtual_path("periodes.py"))
@python_mime
@lru_cache()
def periode_api():
    """
    Virtual ``periodes.py`` file with list of possible periodes values in
    variable ``periode_list``.
    """
    periodes = read_template("periode.txt").decode("utf-8")

    return PY_HEADER + "periode_list = %s.splitlines()\n\n" % repr(periodes)
