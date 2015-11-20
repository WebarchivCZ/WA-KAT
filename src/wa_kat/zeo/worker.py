#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time

import transaction


# Functions & classes =========================================================
def worker(url, property_info, filler_params):
    from .request_database import RequestDatabase

    db = RequestDatabase()
    req = db.get_request(url)

    # this may take some time, hence outside transaction manager
    data = property_info.filler_func(*filler_params)

    with transaction.manager:
        val = getattr(req, property_info.name)

        if val is not None:
            val.extend(data)
        else:
            setattr(req, property_info.name, data)

        req.processing_ended_ts = time.time()
        req._p_changed = True
