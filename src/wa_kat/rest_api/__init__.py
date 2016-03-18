#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import traceback
from os.path import join
from StringIO import StringIO

import requests  # for requests.exceptions.Timeout

from bottle import post
from bottle import response
from bottle import HTTPError
from bottle_rest import form_to_params

from .. import settings
from ..zeo import RequestDatabase
from ..settings import API_PATH

from shared import RESPONSE_TYPE


# Other API modules
import aleph_api
import virtual_fs
from to_output import to_output
from keywords import get_kw_list


# Functions & classes =========================================================
@post(join(API_PATH, "analyze"))
@form_to_params
def analyzer_api(url):
    rd = RequestDatabase()
    response.content_type = RESPONSE_TYPE

    # handle cacheing
    ri = rd.get_request(url)

    try:

        if ri.is_old():
            print "Running the analysis"  #: TODO: to log

            # forget the old one and create new request info - this prevents
            # conflict errors
            ri = rd.get_request(url, new=True)

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
            timeout=settings.REQUEST_TIMEOUT,
            message=str(e.message)
        )

        return {
            "status": False,
            "log": ri.get_log(),
            "error": error_msg,
        }
    except Exception as e:
        return {
            "status": False,
            "log": ri.get_log(),
            "error": str(e.message) + "\n" + traceback.format_exc().strip()
        }

    return {
        "status": True,
        "body": ri.to_dict(),
        "log": ri.get_log(),
    }


@post(join(API_PATH, "as_file/<fn:path>"))
@form_to_params(return_json=False)
def download_as_file(fn, data=None):
    if data is None:
        raise HTTPError(500, "This service require POST `data` parameter.")

    response.set_header("Content-Type", "application/octet-stream")
    response.set_header(
        "Content-Disposition",
        'attachment; filename="%s"' % fn
    )

    return StringIO(data)
