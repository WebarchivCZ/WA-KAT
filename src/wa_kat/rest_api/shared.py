#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Functions / constants shared across the REST API.
"""
#
# Imports =====================================================================
import os
import gzip
import json
import time
import os.path
import StringIO

from bottle import request
from bottle import response
from bottle import parse_date
from bottle import HTTPResponse


# Variables ===================================================================
JSON_MIME = "application/json; charset=utf-8"


# Functions ===================================================================
def to_gzipped_file(data, out=None):
    """
    Pack `data` to GZIP and write them to `out`. If `out` is not defined,
    :mod:`stringio` is used.

    Args:
        data (obj): Any packable data (str / unicode / whatever).
        out (file, default None): Optional opened file handler.

    Returns:
        obj: File handler with packed data seeked at the beginning.
    """
    if not out:
        out = StringIO.StringIO()

    with gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(data)

    out.seek(0)
    return out


def gzipped(fn):
    """
    Decorator used to pack data returned from the Bottle function to GZIP.

    The decorator adds GZIP compression only if the browser accepts GZIP in
    it's ``Accept-Encoding`` headers. In that case, also the correct
    ``Content-Encoding`` is used.
    """
    def gzipped_wrapper(*args, **kwargs):
        accepted_encoding = request.get_header("Accept-Encoding")

        if not accepted_encoding or "gzip" not in accepted_encoding:
            return fn(*args, **kwargs)

        response.set_header("Content-Encoding", "gzip")

        return to_gzipped_file(fn(*args, **kwargs))

    return gzipped_wrapper


def gzip_cache(path):
    """
    Another GZIP handler for Bottle functions. This may be used to cache the
    files statically on the disc on given `path`.

    If the browser accepts GZIP and there is file at ``path + ".gz"``, this
    file is returned, correct headers are set (Content-Encoding, Last-Modified,
    Content-Length, Date and so on).

    If the browser doesn't accept GZIP or there is no ``.gz`` file at same
    path, normal file is returned.

    Args:
        path (str): Path to the cached file.

    Returns:
        obj: Opened file.
    """
    accept_enc = request.get_header("Accept-Encoding")

    if accept_enc and "gzip" in accept_enc and os.path.exists(path + ".gz"):
        path = path + ".gz"
        response.set_header("Content-Encoding", "gzip")

    stats = os.stat(path)

    headers = dict()
    headers['Content-Length'] = stats.st_size
    headers['Last-Modified'] = time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT",
        time.gmtime(stats.st_mtime)
    )

    # I need to set `headers` dict for optional HTTPResponse use, but also set
    # hedears using `response.set_header()` for normal use
    for key, val in headers.iteritems():
        response.set_header(key, val)

    modified_since = request.environ.get('HTTP_IF_MODIFIED_SINCE')
    if modified_since:
        modified_since = parse_date(modified_since.split(";")[0].strip())

    if modified_since is not None and modified_since >= int(stats.st_mtime):
        headers['Date'] = time.strftime(
            "%a, %d %b %Y %H:%M:%S GMT",
            time.gmtime()
        )
        return HTTPResponse(status=304, **headers)

    return open(path)


def in_template_path(fn):
    """
    Return `fn` in template context, or in other words add `fn` to template
    path, so you don't need to write absolute path of `fn` in template
    directory manually.

    Args:
        fn (str): Name of the file in template dir.

    Return:
        str: Absolute path to the file.
    """
    return os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "../templates",
        fn,
    )


def read_template(fn):
    """
    Read template `fn` from the template directory.

    Args:
        fn (str): Name of the file in template directory (relative to template
            directory).

    Returns:
        any: Returned data.
    """
    with open(in_template_path(fn)) as f:
        return f.read()


def to_json(data):
    """
    Convert `data` to pretty JSON.

    Args:
        data (any): Any JSON convertable data.

    Returns:
        unicode: Converted data.
    """
    return json.dumps(
        data,
        indent=4,
        separators=(',', ': ')
    )
