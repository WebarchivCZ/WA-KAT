#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================


# Functions & classes =========================================================
class SourceString(str):
    """
    Extended ``str`` class containing also informations about source of the
    string.

    Attributes:
        val (str): Value of the string.
        source (str, default None): Source of the `val`.
    """
    def __new__(self, val, *args, **kwargs):
        try:
            return str.__new__(self, val)
        except UnicodeEncodeError:
            return str.__new__(self, val.encode("utf-8"))

    def __init__(self, val, source=None):
        self.val = val
        self.source = source

    def __repr__(self):
        if not self.source:
            return super(SourceString, self).__repr__()

        return "%s:%s" % (self.source, self.val)

    def to_dict(self):
        """
        Convert yourself to dict.
        """
        return {
            "val": self.val,
            "source": self.source,
        }
