#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from wa_kat.zeo import request_info


# Variables ===================================================================


# Fixtures ====================================================================
@pytest.fixture
def ri_obj():
    return request_info.RequestInfo(url="http://kitakitsune.org")


# Tests =======================================================================
def test_get_req_mapping():
    mappings = request_info._get_req_mapping()

    assert mappings


def test_PropertyInfo():
    pi = request_info.PropertyInfo(1, 2, 3)

    assert pi.name
    assert pi.filler_func
    assert pi.filler_params


def test_RequestInfo(ri_obj):
    assert ri_obj.domain == "kitakitsune.org"
    assert ri_obj.creation_ts

    assert not ri_obj.downloaded_ts
    assert not ri_obj.processing_started_ts
    assert not ri_obj.processing_ended_ts

    for property_name in request_info._get_req_mapping().keys():
        assert hasattr(ri_obj, property_name)

    assert not ri_obj.is_all_set()
    assert ri_obj.progress()[0] == 0

    for property_name in request_info._get_req_mapping().keys():
        setattr(ri_obj, property_name, 1)

    assert ri_obj.is_all_set()
    assert ri_obj.progress()[0] == ri_obj.progress()[1]


def test_RequestInfo_download(ri_obj):
    assert not ri_obj.is_all_set()  # make sure you've got new object

    assert "bystrousak" in ri_obj._download("http://kitakitsune.org")


def test_RequestInfo_paralel_download(ri_obj):
    pass
