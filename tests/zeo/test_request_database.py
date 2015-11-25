#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time

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


# Functions ===================================================================
def circuit_breaker_progress_retry(ri, attempts=20):
    for i in range(attempts):
        try:
            print ri.progress()
            assert ri.is_all_set()
            return
        except AssertionError:
            time.sleep(1)

    raise IOError("Paralel processing took too much time, aborting.")


# Tests =======================================================================
def test_request_database(rdb):
    assert rdb

    # with transaction.manager:
        # assert not rdb.requests

    with pytest.raises(ValueError):
        rdb.get_request("azgabas")

    assert rdb.get_request(TEST_URL)


def test_worker(rdb, request_info, client_conf_path):
    assert request_info.title_tags is None
    request_info.index = """<HTML>
<head>
    <title>Bystroushaak</title>
    </head>
</HTML>
    """

    property_info = _get_req_mapping()["title_tags"]
    worker(
        url_key=request_info.url,
        property_info=property_info,
        filler_params=property_info.filler_params(request_info),
        conf_path=client_conf_path,  # to monkeypatch the zeo client conf path
    )

    # lookup to the request info properties
    with transaction.manager:
        assert request_info.title_tags
        assert isinstance(request_info.title_tags, list)

    # lookup to the database
    request = rdb.get_request(request_info.url)
    assert request.title_tags
    assert isinstance(request.title_tags, list)


def test_RequestInfo_paralel_download(request_info, client_conf_path):
    with transaction.manager:
        assert request_info.url == TEST_URL
        assert not request_info.index
        assert not request_info.is_all_set()
        assert request_info.progress()[0] == 1  # set from test_worker()

    request_info.paralel_processing(client_conf=client_conf_path)

    # wait until the processing of all requests is finished
    circuit_breaker_progress_retry(request_info, attempts=20)

    with transaction.manager:
        assert request_info.url
        assert request_info.domain
        assert request_info.index
        assert request_info.creation_ts
        assert request_info.downloaded_ts
        assert request_info.processing_started_ts
        assert request_info.processing_ended_ts

        assert request_info.is_all_set()
        assert request_info.progress()[0] == request_info.progress()[1]

        set_keys = set(request_info.to_dict()["values"].keys())
        assert set_keys == set(_get_req_mapping().keys())

        assert request_info.to_dict()["values"]["place_tags"]


def test_garbage_collection(rdb):
    with transaction.manager:
        assert rdb.requests

    time.sleep(1)
    rdb.garbage_collection(1)

    with transaction.manager:
        assert not rdb.requests
