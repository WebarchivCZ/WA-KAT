#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is used to connect and interface with the Aleph system used in NK
and NTK:

    - http://aleph.nkp.cz
    - http://aleph.techlib.cz
"""
#
# Imports =====================================================================
from collections import namedtuple

from remove_hairs import remove_hairs
from marcxml_parser import MARCXMLRecord
from edeposit.amqp.aleph import aleph

from ..settings import NTK_ALEPH_URL
from ..data_model import Model
from ..analyzers.source_string import SourceString


# Functions & classes =========================================================
def _first_or_none(array):
    """
    Pick first item from `array`, or return `None`, if there is none.
    """
    if not array:
        return None

    return array[0]


def _add_source(model):
    """
    Go over all attributes in `model` and add :class:`SourceString` to them.

    Args:
        model (obj): :class:`Model` instance.

    Returns:
        obj: :class:`Model` instance with :class:`SourceString` descriptors.
    """
    ignored_keys = {"author_tags", "original_xml", "additional_info"}

    # convert all values to source strings
    source = "Aleph"
    for key, val in model.get_mapping().iteritems():
        if key in ignored_keys:
            continue

        if type(val) in [list, tuple]:
            ss_val = [
                SourceString(item, source).to_dict()
                for item in val
            ]
        else:
            ss_val = [SourceString(val, source).to_dict()]

        setattr(model, key, ss_val)

    return model


def by_issn(issn):
    """
    Query aleph for records with given `issn`.

    Args:
        issn (str): ISSN of the periodical.

    Returns:
        obj: :class:`Model` instances for each record.
    """
    # monkeypatched to allow search in NTK's Aleph
    old_url = aleph.ALEPH_URL
    aleph.ALEPH_URL = NTK_ALEPH_URL
    records = aleph.getISSNsXML(issn, base="STK02")
    aleph.ALEPH_URL = old_url

    # process all records
    for record in records:
        marc = MARCXMLRecord(record)

        # following values were requested by @bjackova in
        # https://github.com/WebArchivCZ/WA-KAT/issues/66
        additional_info = {
            "222": marc.get("222", None),
            "PER": marc.get("PER", None),
            "776": marc.get("776", None),
            "008": marc.get("008", None),
            "alt_end_date": ""  # just reminder that it is filled later
        }
        additional_info = {
            key: val
            for key, val in additional_info.iteritems()
            if val
        }

        # check whether there is alternative date in 008
        alt_end_date = None
        alt_creation_date = None
        if additional_info["008"]:
            # 131114c20139999xr-q||p|s||||||---a0eng-c -> 2013
            alt_creation_date = additional_info["008"][7:11]

            # 131114c20139999xr-q||p|s||||||---a0eng-c -> 9999
            alt_end_date = additional_info["008"][11:15]
            if alt_end_date in ["9999", "****"]:
                alt_creation_date += "-"  # library convention is xxxx-
                alt_end_date = None

            additional_info["alt_end_date"] = alt_end_date

        # parse author
        author = Author.parse_author(marc)

        model = Model(
            url=_first_or_none(
                marc.get("856u")
            ),
            conspect=_first_or_none(
                marc.get("072a")
            ),
            annotation_tags=_first_or_none(
                marc.get("520a")
            ),
            periodicity=_first_or_none(
                marc.get("310a")
            ),
            title_tags=_first_or_none(
                marc.get("222a")
            ),
            subtitle_tags=_first_or_none(
                marc.get("245b")
            ),
            place_tags=remove_hairs(
                _first_or_none(marc.get("260a")) or ""
            ),
            author_tags=author._asdict() if author else None,
            publisher_tags=remove_hairs(
                (
                    _first_or_none(marc.get("260b")) or
                    _first_or_none(marc.get("264b")) or
                    "",
                ),
                ", "
            ),
            creation_dates=_first_or_none(
                marc.get("260c", [alt_creation_date])
            ),
            lang_tags=_first_or_none(
                marc.get("040b")
            ),
            keyword_tags=marc.get("650a07"),
            source_info=_first_or_none(
                marc.get("500a")
            ),
            original_xml=record,
            additional_info=additional_info,
        )

        yield _add_source(model)


class Author(namedtuple("Author", ["name",
                                   "code",
                                   "linked_forms",
                                   "is_corporation",
                                   "record",
                                   "alt_name"])):
    @classmethod
    def parse_author(cls, marc):
        name = None
        code = None
        linked_forms = None
        is_corporation = None
        record = None

        # parse informations from the record
        if marc["100a"]:  # persons
            name = _first_or_none(marc["100a"])
            code = _first_or_none(marc["1007"])
            is_corporation = False
            record = marc.datafields["100"][0]  # transport all fields
        elif marc["110a"]:  # corporations
            name = _first_or_none(marc["110a"])
            code = _first_or_none(marc["1107"])
            linked_forms = marc["410a2 "]
            is_corporation = True
            record = marc.datafields["110"][0]  # transport all fields
        else:
            return None

        # parse linked forms (alternative names)
        linked_forms = marc["410a2 "]

        # put together alt_name
        type_descriptor = ["osoba", "organizace"]
        alt_name = "%s [%s]" % (name, type_descriptor[is_corporation])
        if linked_forms:
            alt_name += " (" + ", ".join(linked_forms) + ")"

        return cls(
            name=name,
            code=code,
            linked_forms=linked_forms,
            is_corporation=is_corporation,
            record=record,
            alt_name=alt_name,
        )

    @classmethod
    def search_by_name(cls, name):
        records = aleph.downloadRecords(
            aleph.searchInAleph("aut", name, False, "wau")
        )

        for record in records:
            marc = MARCXMLRecord(record)

            author = cls.parse_author(marc)

            if author:
                yield author
