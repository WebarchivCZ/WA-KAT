#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is used by workers launched as new processes to send back data they
analyzed in paralel.
"""
# Imports =====================================================================
import json
import time

from bottle import post
from bottle_rest import form_to_params

from ..db.request_info import RequestInfo

from ..logger import logger

from ..settings import _REQUEST_DB_SAVE


# Variables ===================================================================
global DATABASE
DATABASE = {}  #: Temporary, in-memory dict used as database.

DAY = 60 * 60 * 24  #: Amount of seconds in one day.
YEAR = DAY * 356  #: Amount of seconds in one year.


# Functions & classes =========================================================
def get_cached_or_new(url, new=False):
    """
    Look into the database and return :class:`RequestInfo` if the `url` was
    already analyzed, or create and return new instance, if not.

    If the `new` is set to True, always create new instance.

    Args:
        url (str): URL of the analyzed resource.
        new (bool, default False): Force new instance?

    Returns:
        obj: :class:`RequestInfo` instance.
    """
    garbage_collection()

    old_req = DATABASE.get(url)

    if old_req and not new:
        return old_req

    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("Invalid URL `%s`!" % url)

    req = RequestInfo(url=url)
    DATABASE[url] = req

    return req


def garbage_collection(time_limit=YEAR/12.0):
    """
    Collect and remove all :class:`.RequestInfo` objects older than
    `time_limit` (in seconds).

    Args:
        time_limit (float, default YEAR / 2): Collect objects older than
            this limit.
    """
    expired_request_infos = (
        ri for ri in DATABASE.values()
        if ri.creation_ts + time_limit <= time.time()
    )

    for ri in expired_request_infos:
        del DATABASE[ri.url]


# REST API ====================================================================
@post(_REQUEST_DB_SAVE)
@form_to_params
def store_property(url, property_name, value):
    """
    Look into database and store `value` under `property_name` in `url`.

    This is part of the REST API.
    """
    logger.debug(
        "store_property(): Received property_name=%s value=%s" % (
            property_name,
            value,
        ),
        url=url,
    )

    ri = get_cached_or_new(url)
    ri._set_property(property_name, json.loads(value))

    logger.info(
        "store_property(): property_name=%s saved." % (
            property_name,
        ),
        url=url,
    )
