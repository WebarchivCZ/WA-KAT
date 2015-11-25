#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import requests


# Variables ===================================================================



# Fixtures ====================================================================
# @pytest.fixture
# def fixture():
#     pass

# with pytest.raises(Exception):
#     raise Exception()


# Tests =======================================================================
def test_rest(web_port):
    url = "http://localhost:%d/api_v1/analyze" % web_port

    resp = requests.post(url, data={"url": "http://kitakitsune.org"})
    out = resp.json()

    assert out["status"]
