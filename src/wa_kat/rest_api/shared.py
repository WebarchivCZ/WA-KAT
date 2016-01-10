#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import gzip
import StringIO

from bottle import request
from bottle import response


# Variables ===================================================================
API_PATH = "/api_v1/"
RESPONSE_TYPE = "application/json; charset=utf-8"


# Functions ===================================================================
def gzipped(fn):
    def gzipped_wrapper(*args, **kwargs):
        accepted_encoding = request.get_header("Accept-Encoding")

        if not accepted_encoding or "gzip" not in accepted_encoding:
            return fn(*args, **kwargs)

        response.set_header("Content-Encoding", "gzip")

        out = StringIO.StringIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(
                fn(*args, **kwargs)
            )

        out.seek(0)
        return out

    return gzipped_wrapper
