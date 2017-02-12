#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import json
import socket
import sqlite3
import argparse
from os.path import join
from os.path import dirname
from contextlib import contextmanager

sys.path.insert(0, join(dirname(__file__), "../src"))

from wa_kat.settings import LOG_UDP_PORT


# Functions & classes =========================================================
@contextmanager
def create_or_open_database(filename):
    # connect database
    db = sqlite3.connect(filename)
    db.text_factory = sqlite3.OptimizedUnicode
    db.text_factory = str

    # try create tables (success only if not created from previous session)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS Logs(
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ip        VARCHAR(50),
            msg       TEXT,
            long_msg  TEXT,
            level     VARCHAR(20),
            timestamp REAL,
            url       VARCHAR(500)
        );
    """)
    db.commit()

    yield db

    db.close()


def save_to_db(db, ip, data):
    db_cur = db.cursor()
    db_cur.execute("""
        INSERT INTO Logs(
            ip,
            msg,
            long_msg,
            level,
            timestamp,
            url
        ) VALUES(?, ?, ?, ?, ?, ?)
        """,
        (
            ip,
            data["msg"],
            data["long_msg"] or "",
            data["level"],
            data["timestamp"],
            data["url"] or "",
        )
    )
    db.commit()


def address_pair(port):
    return ("localhost", port)


def address_pair_to_str(address_pair):
    return "%s:%d" % address_pair


def run_log_listenner(fn, port, quiet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(address_pair(port))

    def decode_data(data):
        return json.loads(data)

    with create_or_open_database(fn) as db:
        while True:
            data, address = sock.recvfrom(65535)


            try:
                save_to_db(db, address_pair_to_str(address), decode_data(data))
                if not quiet:
                    print data
            except Exception as e:
                sys.stderr.write("%s: %s\n" % (e.__class__.__name__, e))
                sys.stderr.write("Received data: %s" % data)


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        nargs="?",
        default="logs.sqlite",
        help="Name of the SQLite database file. Default `logs.sqlite`."
    )
    parser.add_argument(
        "-p",
        "--port",
        default=LOG_UDP_PORT,
        type=int,
        help="Port for the UDP server. Default %d." % LOG_UDP_PORT
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Be quiet."
    )
    args = parser.parse_args()

    run_log_listenner(fn=args.filename, port=args.port, quiet=args.quiet)
