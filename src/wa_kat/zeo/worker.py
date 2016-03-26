#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Worker definition for analyzers runner. Functions defined there are run as
standalone processes.
"""
#
# Imports =====================================================================
import time
import traceback

import transaction
from ZODB.POSException import ConflictError


# Functions & classes =========================================================
def _save_to_database(req, property_name, data):
    """
    Store `data` under `property_name` in the `req` database object.

    Args:
        req (obj): ZODB database object.
        property_name (str): Name of the property under which the `data` will
            be stored.
        data (obj): Any object.
    """
    with transaction.manager:
        setattr(req, property_name, data)

        req.processing_ended_ts = time.time()
        req._p_changed = True

    req.log("`%s` saved." % property_name)


def worker(url_key, property_name, function, function_arguments,
           conf_path=None):
    """
    This function usually runs as process on the background.

    It runs ``function(*function_arguments)`` and then stores them in ZODB
    in `url_key` under `property_name`.

    Warning:
        This function puts data into DB, isntead of returning them.

    Args:
        url_key (str): Key which will be used for database lookup.
        property_name (str): Name of the property used to store data.
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
