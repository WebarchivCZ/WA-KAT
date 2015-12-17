#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time

import transaction
from ZODB.POSException import ConflictError


# Functions & classes =========================================================
def _save_to_database(req, property_name, data):
    with transaction.manager:
        # val = getattr(req, property_name)
        # if val is not None:
        #     val.extend(data)
        # else:
        setattr(req, property_name, data)

        req.processing_ended_ts = time.time()
        req._p_changed = True


def worker(url_key, property_name, property_function, request_info,
           conf_path=None):
    """
    This function is meant to run as process on the background.

    It runs ``property_info.filler_func(*filler_params)`` and then stores them
    in ZODB under `url_key`.

    Warning:
        This function doesn't return the data, but puts them to database!

    Args:
        url_key (str): Key which will be used for database lookup.
        property_info (obj): :class:`.PropertyInfo` instance.
        filler_params (list): List of parameters for function which will be
            called to retreive data.
        conf_path (str, default None): Optional parameter used by tests to
            redirect the database connections to test's environment.
    """
    # this may take some time, hence outside transaction manager
    try:
        data = property_function(request_info)
    except Exception as e:
        # TODO: log e
        data = []

    # get the RequestInfo object from database
    from .request_database import RequestDatabase
    if conf_path:
        db = RequestDatabase(conf_path=conf_path)
    else:
        db = RequestDatabase()

    # save `data` into RequestInfo object property
    for i in xrange(5):
        try:
            return _save_to_database(db.get_request(url_key), property_name, data)
        except ConflictError:
            time.sleep(0.1)
