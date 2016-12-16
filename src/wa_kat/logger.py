#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================


# Functions & classes =========================================================
class Logger(object):
    def _log(self, message, level):
        print message

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
