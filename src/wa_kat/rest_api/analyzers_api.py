#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Connect REST API with Analyzers runner.
"""
#
# Imports =====================================================================
import traceback
from os.path import join

import requests  # for requests.exceptions.Timeout

from bottle import post
from bottle import response
from bottle_rest import form_to_params

from ..settings import API_PATH
from ..settings import REQUEST_TIMEOUT

from ..logger import logger

from shared import JSON_MIME
from db import get_cached_or_new


# REST API ====================================================================
@post(join(API_PATH, "analyze"))
@form_to_params
def analyzer_api(url):
    """
    Analyze given `url` and return output as JSON.
    """
    response.content_type = JSON_MIME

    # handle cacheing
    ri = get_cached_or_new(url)

    try:

        if ri.is_old():
            logger.info("Running the analysis.")

            # forget the old one and create new request info - this prevents
            # conflict errors
            ri = get_cached_or_new(url, new=True)

            # run the processing
            ri.paralel_processing()

    except (requests.exceptions.Timeout, requests.ConnectionError) as e:
        error_msg = """
            Požadovanou stránku {url} nebylo možné stáhnout během {timeout}
            vteřin. Zkuste URL zadat s `www.`, či zkontrolovat funkčnost
            stránek.
            <span style="display: none">{message}</span>
        """
        error_msg = error_msg.format(
            url=url,
            timeout=REQUEST_TIMEOUT,
            message=str(e.message)
        )
        logger.error(error_msg)

        return {
            "status": False,
            "log": "",  # TODO: get real log
            "error": error_msg,
        }
    except Exception as e:
        error_msg = str(e.message) + "\n" + traceback.format_exc().strip()
        logger.error(error_msg)
        return {
            "status": False,
            "log": "ri.get_log()",
            "error": error_msg,
        }

    return {
        "status": True,
        "body": ri.to_dict(),
        "log": "ri.get_log()",
    }
