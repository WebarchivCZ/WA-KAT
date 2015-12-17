#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from remove_hairs import remove_hairs
from marcxml_parser import MARCXMLRecord
from edeposit.amqp.aleph import aleph

from ..data_model import Model


# Variables ===================================================================
# Functions & classes =========================================================
def _first_or_none(array):
    if not array:
        return None

    return array[0]


def by_issn(issn):
    for record in aleph.getISSNsXML(issn):
        marc = MARCXMLRecord(record)

        # Model()
        # TODO: přepsat na .get(), tohle bude vyhazovat výjimky
        conspect = _first_or_none(marc["072a"])
        url = _first_or_none(marc["856u"])
        anotace = _first_or_none(marc["520a"])
        nazev = _first_or_none(marc["222a"])
        misto = remove_hairs(_first_or_none(marc["260a"]))
        vydavatel = remove_hairs(_first_or_none(marc["260b"]), ", ")
        datum = _first_or_none(marc["260c"])
        periodicita = _first_or_none(marc["310a"])
        jazyk = _first_or_none(marc["040b"])
        tagy = marc["650a07"]

        print "---"
        print "conspect:", conspect
        print "url:", url
        print "anotace:", anotace
        print "nazev:", nazev
        print "misto:", misto
        print "vydavatel:", vydavatel
        print "datum:", datum
        print "periodicita:", periodicita
        print "jazyk:", jazyk
        print "tagy:", tagy
