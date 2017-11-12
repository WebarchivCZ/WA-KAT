#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from wa_kat.rest_api.to_output import _to_date_in_588


def test_url_to_fn():
    pass


def test_parse_date_range():
    pass


def test_to_date_in_588():
    assert _to_date_in_588("03.05.2017") == "3.5.2017"

    assert _to_date_in_588("2017.05.03") == "2017.5.3"
