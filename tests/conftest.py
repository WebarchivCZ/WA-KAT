#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import random
import os.path
import threading
import subprocess

import pytest
import requests

# from zeo_connector_defaults import CLIENT_CONF_PATH  # TODO: rewrite to tmp_context
from zeo_connector_defaults import tmp_context_name
from zeo_connector_defaults import generate_environment
from zeo_connector_defaults import cleanup_environment


# Variables ===================================================================
PORT = random.randint(20000, 60000)
URL = "http://127.0.0.1:%d" % PORT
API_URL = URL + "/api/v1/"
_SERVER_HANDLER = None


# Functions ===================================================================
def circuit_breaker_http_retry():
    for i in range(10):
        try:
            return requests.get(URL).raise_for_status()
        except Exception:
            time.sleep(1)

    raise IOError("Couldn't connect to thread with HTTP server. Aborting.")


# Setup =======================================================================
@pytest.fixture(scope="session", autouse=True)
def zeo(request):
    generate_environment()
    request.addfinalizer(cleanup_environment)


@pytest.fixture()
def client_conf_path():
    return tmp_context_name("zeo_client.conf")


@pytest.fixture(scope="session", autouse=True)
def web_port():
    return PORT


@pytest.fixture(scope="session", autouse=True)
def web_url():
    return URL


@pytest.fixture(scope="session", autouse=True)
def web_api_url():
    return API_URL


# @pytest.fixture(scope="session", autouse=True)
# def bottle_server(request, zeo):
#     # run the bottle REST server
#     def run_bottle():
#         command_path = os.path.join(
#             os.path.dirname(__file__),
#             "../../bin/edeposit_rest_webserver.py"
#         )

#         assert os.path.exists(command_path)

#         global _SERVER_HANDLER
#         _SERVER_HANDLER = subprocess.Popen([
#             command_path,
#             "--zeo-client-conf-file", CLIENT_CONF_PATH,
#             "--port", str(PORT),
#             "--host", "127.0.0.1",
#             "--server", "paste",
#             "--debug",
#             "--quiet",
#         ])

#     serv = threading.Thread(target=run_bottle)
#     serv.setDaemon(True)
#     serv.start()

#     circuit_breaker_http_retry()

#     def shutdown_server():
#         _SERVER_HANDLER.terminate()

#     request.addfinalizer(shutdown_server)
