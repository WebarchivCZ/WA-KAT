#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import document


# Functions & classes =========================================================
class KeywordListHandler(object):
    div_el = document["keyword_list"]
    whole_el = document["whole_keyword_list"]

    keywords = []
    _remover = """
        <span class='kw_remover'
              title='Odstranit klíčové slovo.'
              id='kw_remover_id_%d'>
            ✖
        </span>
    """

    @classmethod
    def _render(cls):
        if cls.keywords:
            cls.whole_el.style.display = "block"
        else:
            cls.whole_el.style.display = "none"

        html_lines = (
            "<li class='kw_enum'>{0} {1}</li>\n".format(
                keyword,
                (cls._remover % cnt)
            )
            for cnt, keyword in enumerate(cls.keywords)
        )

        cls.div_el.innerHTML = "<ol>\n%s\n</ol>\n" % "\n".join(html_lines)

        for cnt, keyword in enumerate(cls.keywords):
            uid = "kw_remover_id_%d" % cnt
            el = document[uid]
            el.bind("click", lambda x: cls.remove_keyword(keyword))

    @classmethod
    def add_keyword(cls, keyword):
        cls.keywords.append(keyword)
        cls._render()

    @classmethod
    def remove_keyword(cls, keyword):
        cls.keywords.remove(keyword)
        cls._render()
