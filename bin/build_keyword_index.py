#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import json
import os.path
import argparse

import retrying
import timeout_wrapper
from tqdm import tqdm
from sqlitedict import SqliteDict
from marcxml_parser import MARCXMLRecord
from edeposit.amqp.aleph import aleph
from edeposit.amqp.aleph.aleph import DocumentNotFoundException
from edeposit.amqp.aleph.aleph import InvalidAlephBaseException


# Variables ===================================================================
MAX_RETRY = 20  # how many times to try until the script say that this is end
MAX_DOC_ID = 10000000


# Functions & classes =========================================================
class KeywordInfo(object):
    def __init__(self, uid, sysno, zahlavi, odkazovana_forma, angl_ekvivalent,
                 poznamka):
        self.uid = uid
        self.sysno = sysno
        self.zahlavi = zahlavi
        self.odkazovana_forma = odkazovana_forma
        self.angl_ekvivalent = angl_ekvivalent
        self.poznamka = poznamka

    @classmethod
    def from_marc(cls, sysno, marc):
        def first_or_none(item):
            if not item:
                return None

            if type(item) in [tuple, list]:
                return item[0]

            return item

        return cls(
            uid=first_or_none(marc["001"]),
            sysno=sysno,
            zahlavi=first_or_none(marc["150a"]),
            odkazovana_forma=marc.get("450a", []),
            angl_ekvivalent=first_or_none(marc["750a07"]),
            poznamka=first_or_none(marc["680i"]),
        )

    def to_dict(self):
        return self.__dict__.copy()


@retrying.retry(stop_max_attempt_number=3)
@timeout_wrapper.timeout(5)
def _download(doc_id):
    return aleph.downloadMARCOAI(str(doc_id), "aut10")


def _download_items(db, last_id):
    not_found_cnt = 0
    for doc_id in xrange(last_id, MAX_DOC_ID):
        doc_id += 1
        print "Downloading %d.." % (doc_id)

        if not_found_cnt >= MAX_RETRY:
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
        db["last_id"] = doc_id - MAX_RETRY if doc_id > MAX_RETRY else 1

        if doc_id % 100 == 0:
            db.commit()


def download_items(output_fn, start=None):
    with SqliteDict(output_fn) as db:
        last_id = db.get("last_id", 0) if not start else start
        _download_items(db, last_id)
        db.commit()


def _generate(db):
    for key, val in tqdm(db.iteritems(), total=len(db)):
        # skip counter of the last downloaded document
        if key == "last_id":
            continue

        piece = val[:1000] if len(val) > 1000 else val
        if '<fixfield id="001">ph' not in piece:
            continue

        parsed = MARCXMLRecord(val)

        if not parsed["001"]:
            continue

        if parsed["001"].lower().startswith("ph"):
            yield KeywordInfo.from_marc(
                sysno=int(key.split("_")[-1]),  # item_xxx -> int(xxx)
                marc=parsed,
            )


def generate(output_fn):
    if not os.path.exists(output_fn):
        print >> sys.stderr, "Can't access `%s`!" % output_fn
        sys.exit(1)

    with SqliteDict(output_fn) as db:
        items = [
            item.to_dict()
            for item in _generate(db)
        ]

        with open("index.json", "wt") as f:
            f.write(json.dumps(items))


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Aleph keyword index builder. This program may be used to
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
    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Don't download, only generate data from dataset."
    )

    args = parser.parse_args()

    if not args.generate:
        download_items(args.output, start=args.start_at)

    generate(args.output)
