#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import transaction

from wa_kat.zeo import RequestDatabase


# Variables ===================================================================
TEST_URL = "http://kitakitsune.org"


# Fixtures ====================================================================
@pytest.fixture
def rdb(client_conf_path):
    return RequestDatabase(conf_path=client_conf_path)


@pytest.fixture
def request_info(rdb):
    return rdb.get_request(TEST_URL)


# Tests =======================================================================
def test_request_database(rdb):
    assert rdb

    with transaction.manager:
        assert not rdb.requests

    with pytest.raises(ValueError):
        rdb.get_request("azgabas")

    assert rdb.get_request(TEST_URL)


# def test_RequestInfo_paralel_download(request_info):
#     pass
