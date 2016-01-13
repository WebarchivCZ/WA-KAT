#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import traceback

import transaction
from ZODB.POSException import ConflictError


# Functions & classes =========================================================
def _save_to_database(req, property_name, data):
    with transaction.manager:
        setattr(req, property_name, data)

        req.processing_ended_ts = time.time()
        req._p_changed = True

    req.log("`%s` saved." % property_name)


def worker(url_key, property_name, function, function_arguments,
           conf_path=None):
    """
    This function is meant to run as process on the background.

    It runs ``property_info.filler_func(*filler_params)`` and then stores them
    in ZODB under `url_key`.

    Warning:
        This function doesn't return the data, but puts them to database!

    Args:
        url_key (str): Key which will be used for database lookup.
        function (obj): Function used to load the data.
        function_arguments (list): List of parameters for function which will
            be called to retreive data.
        conf_path (str, default None): Optional parameter used by tests to
            redirect the database connections to test's environment.
    """
    # this may take some time, hence outside transaction manager
    error_msg = None
    try:
        data = function(*function_arguments)
    except Exception as e:
        data = []
        error_msg = "Error: " + traceback.format_exc().strip()
        error_msg += "\n" + str(e.message)

        with open("/home/bystrousak/wa_error.log", "a") as f:
            f.write(error_msg)

    # get the RequestInfo object from database
    from .request_database import RequestDatabase
    if conf_path:
        db = RequestDatabase(conf_path=conf_path)
    else:
        db = RequestDatabase()

    # save `data` into RequestInfo object property
    for i in xrange(5):
        # resolve the request_info object
        request_info = db.get_request(url_key)

        # handle logging of possible error message
        if error_msg:
            request_info.log(error_msg)
            error_msg = None

        func_name = str(function.__name__)
        request_info.log("Attempting to save output from `%s`." % func_name)

        # attempt to save the data into database
        try:
            return _save_to_database(
                req=request_info,
                property_name=property_name,
                data=data
            )
        except ConflictError:
            request_info.log("Attempt to save `%s` failed." % func_name)
            time.sleep(0.1)
