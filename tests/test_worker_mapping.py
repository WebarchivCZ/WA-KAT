#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.worker_mapping import PropertyInfo
from wa_kat.worker_mapping import worker_mapping


# Tests =======================================================================
def test_worker_mapping():
    assert worker_mapping()


def test_PropertyInfo():
    pi = PropertyInfo(1, 2, 3)

    assert pi.name
    assert pi.filler_func
    assert pi.filler_params
