#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import traceback

from .settings import ERROR_LOG_PATH


# Functions & classes =========================================================
class Logger(object):
    def _log(self, msg, long_msg, level, url=None):
        logged_obj = {
            "msg": msg,
            "long_msg": long_msg,
            "level": level,
            "timestamp": time.time(),
            "url": url
        }

        with open(ERROR_LOG_PATH, "a") as f:
            f.write(
                "{timestamp} {level} {url}: {msg}\n{long_msg}\n".format(
                    **logged_obj
                )
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


logger = Logger()


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
