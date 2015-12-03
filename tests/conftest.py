#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import time
import random
import os.path
import tempfile
import threading
import subprocess

import pytest
import requests

from zeo_connector_defaults import tmp_context_name
from zeo_connector_defaults import generate_environment
from zeo_connector_defaults import cleanup_environment


# Variables ===================================================================
PORT = random.randint(20000, 60000)
URL = "http://127.0.0.1:%d" % PORT
API_URL = URL + "/api/v1/"
_SERVER_HANDLER = None


# Functions ===================================================================
def circuit_breaker_http_retry(max_retry=10):
    for i in range(max_retry):
        try:
            print "Connecting to server .. %d/%d" % (i + 1, max_retry)
            return requests.get(URL).raise_for_status()
        except Exception:
            time.sleep(1)

    raise IOError("Couldn't connect to thread with HTTP server. Aborting.")


def _create_alt_settings(path):
    alt_settings = {
        "ZEO_CLIENT_PATH": path,

        "WEB_ADDR": "127.0.0.1",
        "WEB_PORT": web_port(),
        "WEB_SERVER": "paste",
        "WEB_DEBUG": True,
        "WEB_RELOADER": True,
        "WEB_BE_QUIET": True,
    }

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(json.dumps(alt_settings))
        return f.name


# Setup =======================================================================
@pytest.fixture(scope="session", autouse=True)
def zeo(request):
    generate_environment()
    request.addfinalizer(cleanup_environment)


@pytest.fixture(scope="session", autouse=True)
def client_conf_path(zeo):
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


@pytest.fixture(scope="session", autouse=True)
def bottle_server(request, zeo, client_conf_path):
    alt_conf_path = _create_alt_settings(client_conf_path)

    # run the bottle REST server
    def run_bottle():
        # prepare path to the command
        command_path = os.path.join(
            os.path.dirname(__file__),
            "../bin/run_wa_kat_server.py"
        )
        assert os.path.exists(command_path)

        # replace settings with mocked file
        my_env = os.environ.copy()
        my_env["SETTINGS_PATH"] = alt_conf_path

        # run the server
        global _SERVER_HANDLER
        _SERVER_HANDLER = subprocess.Popen(command_path, env=my_env)

    serv = threading.Thread(target=run_bottle)
    serv.setDaemon(True)
    serv.start()

    # add finalizer which shutdowns the server and remove temporary file
    def shutdown_server():
        _SERVER_HANDLER.terminate()
        os.unlink(alt_conf_path)

    request.addfinalizer(shutdown_server)

    # wait until the connection with server is created
    circuit_breaker_http_retry()
