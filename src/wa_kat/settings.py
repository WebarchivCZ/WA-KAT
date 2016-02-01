#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
Module is containing all necessary global variables for the package.

Module also has the ability to read user-defined data from following paths:

- ``SETTINGS_PATH`` env variable file pointer to .json file.
- ``$HOME/_SETTINGS_PATH``
- ``/etc/_SETTINGS_PATH``

See :attr:`_SETTINGS_PATH` for details.

Note:
    When the first path is found, others is ignored.

Example of the configuration file (``$HOME/webarchive/wa_kat.json``)::

    {
        "WEB_ADDR": "somedomain.cz",
        "WEB_PORT": 80
    }

Example of starting the program with env variable::

    export WA_KAT_SETTINGS="/tmp/conf.json"; bin/run_wa_kat_server.py

Attributes
----------
"""
# Imports =====================================================================
import os
import json
import os.path


# Module configuration ========================================================
#: Path to the file with zeo_client.conf.
ZEO_CLIENT_PATH = "/etc/wa_kat/zeo_client.conf"
PROJECT_KEY = "wa_kat"  #: This is used in ZODB. DON'T CHANGE THIS.
ZEO_CACHE_TIME = 60 * 30  #: ZEO cache time - 30 minutes.
ZEO_MAX_WAIT_TIME = 60 * 5  #: Time after which the processing is restarted. 5m

WEB_ADDR = "localhost"  #: Address where the webserver should listen.
WEB_PORT = 8080  #: Port for the webserver.
WEB_SERVER = 'paste'  #: Use `paste` for threading.
WEB_DEBUG = False  #: Turn on web debug messages?
WEB_RELOADER = False  #: Turn on reloader for webserver?
WEB_BE_QUIET = False  #: Be quiet and don't emit debug messages to terminal.

REMOTE_INFO_URL = "http://%s:%d/remote_info_mock" % (WEB_ADDR, WEB_PORT)  # TODO: fix
REQUEST_TIMEOUT = 5
TIMEOUT_MESSAGE = "Požadovanou stránku nebylo možné stáhnout. Zkuste url s www."

GUI_TO_REST_PERIODE = 2  #: How often check the REST API.


# User configuration reader (don't edit this) =================================
_ALLOWED = [str, unicode, int, float, long, bool]  #: Allowed types.
_SETTINGS_PATH = "webarchive/wa_kat.json"  #: Appended to default search paths.


def _get_all_constants():
    """
    Get list of all uppercase, non-private globals (doesn't start with ``_``).

    Returns:
        list: Uppercase names defined in `globals()` (variables from this \
              module).
    """
    return [
        key for key in globals().keys()
        if all([
            not key.startswith("_"),          # publicly accesible
            key.upper() == key,               # uppercase
            type(globals()[key]) in _ALLOWED  # and with type from _ALLOWED
        ])
    ]


def _substitute_globals(config_dict):
    """
    Set global variables to values defined in `config_dict`.

    Args:
        config_dict (dict): dict with data, which are used to set `globals`.

    Note:
        `config_dict` have to be dictionary, or it is ignored. Also all
        variables, that are not already in globals, or are not types defined in
        :attr:`_ALLOWED` (str, int, ..) or starts with ``_`` are silently
        ignored.
    """
    if not isinstance(config_dict, dict):
        raise ValueError("Configuration file must be contained in dictionary!")

    constants = _get_all_constants()
    for key, val in config_dict.iteritems():
        if key in constants and type(val) in _ALLOWED:
            globals()[key] = val


def _assert_constraints():
    def _format_error(var_name, msg):
        msg = repr(msg) if msg else "UNSET!"
        return "You have to set %s (%s) in rest.json config!" % (var_name, msg)

    def _assert_var_is_set(var_name):
        assert globals()[var_name], _format_error(
            var_name,
            globals()[var_name]
        )

    def _assert_exists_and_perm(var, path, perm):
        msg = "Can't access the required `%s` " % path
        msg += "file set in configuration (%s)!" % var

        assert os.path.exists(path) and os.access(path, perm), msg

    _assert_var_is_set("ZEO_CLIENT_PATH")
    _assert_exists_and_perm("ZEO_CLIENT_PATH", ZEO_CLIENT_PATH, os.R_OK)


def _read_from_paths():
    """
    Try to read data from configuration paths ($HOME/_SETTINGS_PATH,
    /etc/_SETTINGS_PATH).
    """
    home = os.environ.get("HOME", "")
    home_path = os.path.join(home, _SETTINGS_PATH)
    etc_path = os.path.join("/etc", _SETTINGS_PATH)
    env_path = os.environ.get("SETTINGS_PATH", "")

    read_path = None
    if env_path and os.path.exists(env_path):
        read_path = env_path
    elif home and os.path.exists(home_path):
        read_path = home_path
    elif os.path.exists(etc_path):
        read_path = etc_path

    if not read_path:
        return "{}"

    with open(read_path) as f:
        return f.read()


def _apply_settings():
    """
    Read variables from the possible paths. Assert that constraints are set.
    """
    _substitute_globals(
        json.loads(_read_from_paths())
    )

    if not os.environ.get('READTHEDOCS'):
        _assert_constraints()


_apply_settings()
