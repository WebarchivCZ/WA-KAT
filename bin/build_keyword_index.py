#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import argparse
from contextlib import contextmanager

import retrying
import timeout_wrapper
from sqlitedict import SqliteDict
from marcxml_parser import MARCXMLRecord
from edeposit.amqp.aleph import aleph
from edeposit.amqp.aleph.aleph import DocumentNotFoundException
from edeposit.amqp.aleph.aleph import InvalidAlephBaseException


# Variables ===================================================================
MAX_DOC_ID = 1000000


# Functions & classes =========================================================
@retrying.retry(stop_max_attempt_number=3)
@timeout_wrapper.timeout(5)
def _download(doc_id):
    return aleph.downloadMARCOAI(str(doc_id), "aut10")


def _download_items(db, last_id):
    not_found_cnt = 0
    for doc_id in xrange(last_id, MAX_DOC_ID):
        doc_id += 1
        print "Downloading %d.." % (doc_id)

        if not_found_cnt >= 20:
            print "It looks like this is an end:", doc_id
            break

        try:
            record = _download(doc_id)
        except (DocumentNotFoundException, InvalidAlephBaseException):
            print "\tnot found, skipping"
            not_found_cnt += 1
            continue

        not_found_cnt = 0
        db["item_%d" % doc_id] = record
        db["last_id"] = doc_id - 1

        if doc_id % 100 == 0:
            db.commit()


def build_index(output_fn, start=None):
    with SqliteDict(output_fn) as db:
        last_id = db.get("last_id", 0) if not start else start
        _download_items(db, last_id)
        db.commit()

        # parsed = MARCXMLRecord(record)

        # if not parsed["001"]:
            # continue

        # if parsed["001"].lower().startswith("ph"):
            # print "\tsaved"


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Aleph keyword index builder. This program may be used to \
    build fast index for the keywords from AUT base."""
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./aleph_kw_index.sqlite",
        help="Name of the index file."
    )
    parser.add_argument(
        "-s",
        "--start-at",
        metavar="N",
        dest="start_at",
        type=int,
        help="Start from N instead of last used value."
    )

    args = parser.parse_args()

    build_index(args.output, start=args.start_at)
