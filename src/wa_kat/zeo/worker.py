#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time

import transaction


# Functions & classes =========================================================
def worker(url, property_info, filler_params, conf_path=None):
    from .request_database import RequestDatabase

    # this may take some time, hence outside transaction manager
    data = property_info.filler_func(*filler_params)

    db = RequestDatabase(conf_path=conf_path)
    req = db.get_request(url)

    with transaction.manager:
        val = getattr(req, property_info.name)

        if val is not None:
            val.extend(data)
        else:
            setattr(req, property_info.name, data)

        req.processing_ended_ts = time.time()
        req._p_changed = True
