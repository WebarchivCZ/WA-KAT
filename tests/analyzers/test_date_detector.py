#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from wa_kat.analyzers.creation_date_detector import TimeResource
from wa_kat.analyzers.creation_date_detector import mementoweb_api_tags
from wa_kat.analyzers.creation_date_detector import get_whois_tags
from wa_kat.analyzers.creation_date_detector import get_creation_date_tags


# Tests =======================================================================
def test_kitakitsune_mementoweb():
    memento_tags = mementoweb_api_tags("kitakitsune.org")

    assert memento_tags


def test_kitakitsune_whois():
    whois_tags = get_whois_tags("kitakitsune.org")

    assert whois_tags[0].url == "http://whois.icann.org/en/lookup?name=kitakitsune.org"
    assert whois_tags[0].date == "2009-03-27T04:04:05"
    assert whois_tags[0].val == "2009"
    assert whois_tags[0].source == "Whois"
