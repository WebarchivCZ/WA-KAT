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
    def _log(self, message, level):
        print message

        with open(ERROR_LOG_PATH, "a") as f:
            f.write("%f %s: %s\n" % (time.time(), level.upper(), message))

    def emergency(self, message):
        self._log(message, "emergency")

    def alert(self, message):
        self._log(message, "alert")

    def critical(self, message):
        self._log(message, "critical")

    def error(self, message):
        self._log(message, "error")

    def warning(self, message):
        self._log(message, "warning")

    def notice(self, message):
        self._log(message, "notice")

    def info(self, message):
        self._log(message, "info")

    def debug(self, message):
        self._log(message, "debug")


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
                    e.__name__,
                    fn.__name__,
                    args,
                    kwargs,
                    e.__str__(),
                )
            )
            raise

    return log_exception_decorator
