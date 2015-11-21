#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import transaction

from wa_kat.zeo import RequestDatabase
from wa_kat.zeo.worker import worker
from wa_kat.zeo.request_info import _get_req_mapping


# Variables ===================================================================
TEST_URL = "http://kitakitsune.org"


# Fixtures ====================================================================
@pytest.fixture
def rdb(client_conf_path):
    return RequestDatabase(conf_path=client_conf_path)


@pytest.fixture
def request_info(client_conf_path):
    # make sure, that new object is created and thus it is indeed new
    # connection to database
    return rdb(client_conf_path).get_request(TEST_URL)


# Tests =======================================================================
def test_request_database(rdb):
    assert rdb

    with transaction.manager:
        assert not rdb.requests

    with pytest.raises(ValueError):
        rdb.get_request("azgabas")

    assert rdb.get_request(TEST_URL)


def test_worker(request_info, client_conf_path):
    assert request_info.title_tags is None
    request_info.index = """<HTML>
<head>
    <title>Bystroushaak</title>
    </head>
</HTML>
    """

    property_info = _get_req_mapping()["title_tags"]
    worker(
        request_info.url,
        property_info,
        property_info.filler_params(request_info),
        client_conf_path,  # to monkeypatch the path to the zeo client conf
    )

    assert request_info.title_tags
    assert isinstance(request_info.title_tags, list)


def test_RequestInfo_paralel_download(request_info):
    assert request_info.url == TEST_URL
    assert not request_info.index
