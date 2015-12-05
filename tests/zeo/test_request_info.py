#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from wa_kat.zeo import request_info
from wa_kat.worker_mapping import worker_mapping


# Variables ===================================================================


# Fixtures ====================================================================
@pytest.fixture
def ri_obj():
    return request_info.RequestInfo(url="http://kitakitsune.org")


# Tests =======================================================================
def test_RequestInfo(ri_obj):
    assert ri_obj.domain == "kitakitsune.org"
    assert ri_obj.creation_ts

    assert not ri_obj.downloaded_ts
    assert not ri_obj.processing_started_ts
    assert not ri_obj.processing_ended_ts

    for property_name in request_info.worker_mapping().keys():
        assert hasattr(ri_obj, property_name)

    assert not ri_obj.is_all_set()
    assert ri_obj.progress()[0] == 0

    for property_name in request_info.worker_mapping().keys():
        setattr(ri_obj, property_name, 1)

    assert ri_obj.is_all_set()
    assert ri_obj.progress()[0] == ri_obj.progress()[1]


def test_RequestInfo_download(ri_obj):  # TODO: rewrite to use rest
    assert not ri_obj.is_all_set()  # make sure you've got new object

    assert "bystrousak" in ri_obj._download("http://kitakitsune.org")


def test_to_dict(ri_obj):
    out_dict = ri_obj.to_dict()
    keys = request_info.worker_mapping().keys()

    assert out_dict
    assert out_dict["all_set"] == False
    assert out_dict["progress"] == (0, len(keys))

    for key in keys:
        assert key in out_dict["values"]


def test_eq():
    r1 = request_info.RequestInfo(url="http://kitakitsune.org")
    r2 = request_info.RequestInfo(url="http://kitakitsune.org")
    r3 = request_info.RequestInfo(url="http://azgabash.org")

    assert r1 == r2
    assert r2 == r1

    assert r1 != r3
    assert r3 != r1

    assert r2 != r3
    assert r3 != r2


def test_lt():
    r1 = request_info.RequestInfo(url="http://kitakitsune.org")
    r2 = request_info.RequestInfo(url="http://kitakitsune.org")

    assert r1 < r2
