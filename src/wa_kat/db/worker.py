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
import json
import traceback

import requests

from ..logger import logger

from ..settings import _WEB_URL
from ..settings import _REQUEST_DB_SAVE

from ..settings import REQUEST_TIMEOUT


# Functions & classes =========================================================
def _save_to_database(url, property_name, data):
    """
    Store `data` under `property_name` in the `url` key in REST API DB.

    Args:
        url (obj): URL of the resource to which `property_name` will be stored.
        property_name (str): Name of the property under which the `data` will
            be stored.
        data (obj): Any object.
    """
    data = json.dumps([
        d.to_dict() if hasattr(d, "to_dict") else d
        for d in data
    ])

    logger.debug("_save_to_database() data: %s" % repr(data))

    requests.post(
        _WEB_URL + _REQUEST_DB_SAVE,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
        verify=False,
        data={
            "url": url,
            "value": data,
            "property_name": property_name,
        }
    )

    logger.info(
        "`%s` for `%s` sent to REST DB." % (
            property_name,
            url,
        )
    )


def worker(url_key, property_name, function, function_arguments):
    """
    This function usually runs as process on the background.

    It runs ``function(*function_arguments)`` and then stores them in REST API
    storage.

    Warning:
        This function puts data into DB, isntead of returning them.

    Args:
        url_key (str): Key which will be used for database lookup.
        property_name (str): Name of the property used to store data.
        function (obj): Function used to load the data.
        function_arguments (list): List of parameters for function which will
            be called to retreive data.
        error_log_path (str): If set, log errors into this file, otherwise
            stderr.
    """
    # this may take some time, hence outside transaction manager
    error_msg = None
    try:
        data = function(*function_arguments)
    except Exception as e:
        data = []
        error_msg = "Error: " + traceback.format_exc().strip()
        error_msg += "\n" + str(e.message)

    # handle logging of possible error message
    if error_msg:
        logger.error(error_msg)
        error_msg = None

    func_name = str(function.__name__)
    logger.info(
        "Attempting to save output from `%s`." % func_name
    )

    # save `data` into RequestInfo object property
    return _save_to_database(
        url=url_key,
        property_name=property_name,
        data=data
    )
