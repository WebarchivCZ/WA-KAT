#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import time
from os.path import join

from bottle import get
from bottle import post
from bottle_rest import form_to_params

from ..db.request_info_no_db import RequestInfo

from ..logger import logger

from ..settings import API_PATH
from ..settings import _REQUEST_DB_SAVE


# Variables ===================================================================
DATABASE = {}
global DATABASE

DAY = 60 * 60 * 24  #: Amount of seconds in one day.
YEAR = DAY * 356  #: Amount of seconds in one year.


# Functions & classes =========================================================
def get_cached_or_new(url, new=False):
    old_req = DATABASE.get(url)

    if old_req and not new:
        return old_req

    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("Invalid URL `%s`!" % url)

    req = RequestInfo(url=url)
    DATABASE[url] = req

    return req


def garbage_collection(time_limit=YEAR/12.0):
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
    logger.debug("store_property(): Received url=%s property_name=%s value=%s" % (
        url,
        property_name,
        value,
    ))

    ri = get_cached_or_new(url)
    ri._set_property(property_name, json.loads(value))

    logger.info(
        "store_property(): Data for %s (property_name=%s) saved." % (
            url,
            property_name,
        )
    )
