#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from iso3166 import countries
from iso_639_codes import translate


# Functions & classes =========================================================
def normalize(code):
    """
    Normalize language codes using ISO conversion. If all conversions fails,
    return the `code`.

    Args:
        code (str): Language / country code.

    Returns:
        str: ISO 639-2 country code.
    """
    if len(code) == 3:
        return code

    normalized = translate(code)

    if normalized:
        return normalized

    country = countries.get(code, None)

    if country:
        return country.alpha3.lower()

    return code
