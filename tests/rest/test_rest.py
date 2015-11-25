#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import requests


# Fixtures ====================================================================
@pytest.fixture
def analyze_url(web_port):
    return "http://localhost:%d/api_v1/analyze" % web_port


# Tests =======================================================================
def test_rest(analyze_url):
    resp = requests.post(analyze_url, data={"url": "http://kitakitsune.org/"})
    out = resp.json()

    assert out["status"]
    assert "error" not in out
    assert "body" in out

    assert "all_set" in out["body"]
    assert "progress" in out["body"]
    assert "values" in out["body"]


def test_rest_fail(analyze_url):
    resp = requests.post(analyze_url, data={"url": "azgabash"})
    out = resp.json()

    assert not out["status"]
    assert "error" in out
    assert out["error"]
