#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import time
import socket
import traceback

from .settings import SENTRY_DSN
from .settings import LOG_TO_SENTRY

from .settings import LOG_TO_FILE
from .settings import ERROR_LOG_PATH

from .settings import LOG_TO_STDOUT

from .settings import LOG_VIA_UDP
from .settings import LOG_UDP_ADDR
from .settings import LOG_UDP_PORT


# Functions & classes =========================================================
class Logger(object):
    def __init__(self, url=None):
        self.url = url

        self.log_path = None

        self.udp_address = None
        self.udp_port = None

        self.sentry_dsn = None

        self.should_log_to_file = False
        self.should_log_via_udp = False
        self.should_log_to_sentry = False
        self.should_log_to_stdout = True

        self.sentry_client = None

    def use_file(self, log_path):
        self.log_path = log_path
        self.should_log_to_file = True

    def use_udp(self, address, port):
        self.udp_address = address
        self.udp_port = port
        self.should_log_via_udp = True

    def use_sentry(self, sentry_dsn):
        from raven import Client
        self.sentry_client = Client(SENTRY_DSN)
        self.should_log_to_sentry = True

    def _log(self, msg, long_msg, level, url=None):
        logged_obj = {
            "msg": msg,
            "long_msg": long_msg,
            "level": level,
            "timestamp": time.time(),
            "url": url or self.url
        }

        if self.should_log_via_udp:
            self._log_to_udp(logged_obj)

        if self.should_log_to_file:
            self._log_to_file(logged_obj)

        if self.should_log_to_stdout:
            self._log_to_stdout(logged_obj)

        if self.should_log_to_sentry:
            self._log_to_sentry(logged_obj)

    @property
    def address_pair(self):
        return (self.udp_address, self.udp_port)

    def _log_to_udp(self, logged_obj):
        as_json = json.dumps(logged_obj)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(as_json, self.address_pair)
        except socket.gaierror as e:
            print "ERROR: Can't log to UDP logger - %s" % str(e)
        finally:
            sock.close()

    def _format_obj_to_str(self, logged_obj):
        if logged_obj["url"]:
            log_format = "{timestamp} {level} {url}; {msg}\n"
        else:
            log_format = "{timestamp} {level}; {msg}\n"

        if logged_obj["long_msg"]:
            log_format += "{long_msg}\n"

        return log_format.format(**logged_obj)

    def _log_to_file(self, logged_obj):
        with open(self.log_path, "a") as f:
            f.write(self._format_obj_to_str(logged_obj))

    def _log_to_stdout(self, logged_obj):
        print self._format_obj_to_str(logged_obj)

    def _log_to_sentry(self, logged_obj):
        if not self.sentry_client:
            print "ERROR: Requested Sentry logging, but client is not set!"
            return

        self.sentry_client.captureMessage(
            logged_obj["msg"],
            data=logged_obj,
            level=logged_obj["level"],
        )

    def emergency(self, msg, long_msg=None, url=None):
        self._log(msg, long_msg=long_msg, level="emergency", url=url)

    def alert(self, msg, long_msg=None, url=None):
        self._log(msg, long_msg=long_msg, level="alert", url=url)

    def critical(self, msg, long_msg=None, url=None):
        self._log(msg, long_msg=long_msg, level="critical", url=url)

    def error(self, msg, long_msg=None, url=None):
        self._log(msg, long_msg=long_msg, level="error", url=url)

    def warning(self, msg, long_msg=None, url=None):
        self._log(msg, long_msg=long_msg, level="warning", url=url)

    def notice(self, msg, long_msg=None, url=None):
        self._log(msg, long_msg=long_msg, level="notice", url=url)

    def info(self, msg, long_msg=None, url=None):
        self._log(msg, long_msg=long_msg, level="info", url=url)

    def debug(self, msg, long_msg=None, url=None):
        self._log(msg, long_msg=long_msg, level="debug", url=url)


def set_logger_by_settingspy():
    logger = Logger()

    logger.should_log_to_stdout = LOG_TO_STDOUT

    if LOG_TO_FILE:
        logger.use_file(ERROR_LOG_PATH)

    if LOG_VIA_UDP:
        logger.use_udp(LOG_UDP_ADDR, LOG_UDP_PORT)

    if LOG_TO_SENTRY:
        logger.use_sentry(SENTRY_DSN)

    return logger


logger = set_logger_by_settingspy()


def log_exception(fn):
    def _catch_type_error_from_traceback():
        try:
            return traceback.format_exc().strip()
        except TypeError:
            return "ERROR: Can't recover traceback."

    def log_exception_decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(_catch_type_error_from_traceback())
            logger.error(
                "%s while calling %s(*args=%r, **kwargs%r): %s" % (
                    e.__class__.__name__,
                    fn.__name__,
                    args,
                    kwargs,
                    e.__str__(),
                )
            )
            raise

    return log_exception_decorator
