#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import requests

from ..settings import USER_AGENT
from ..settings import REQUEST_TIMEOUT


# Functions & classes =========================================================
def download(url):
    """
    Download `url` and return it as utf-8 encoded text.

    Args:
        url (str): What should be downloaded?

    Returns:
        str: Content of the page.
    """
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers=headers,
        allow_redirects=True,
        verify=False,
    )

    def decode(st, alt_encoding=None):
        encodings = ['ascii', 'utf-8', 'iso-8859-1', 'iso-8859-15']

        if alt_encoding:
            if isinstance(alt_encoding, basestring):
                encodings.append(alt_encoding)
            else:
                encodings.extend(alt_encoding)

        for encoding in encodings:
            try:
                return st.encode(encoding).decode("utf-8")
            except UnicodeEncodeError, UnicodeDecodeError:
                pass

        raise UnicodeError('Could not find encoding.')

    return decode(resp.text, resp.encoding)
