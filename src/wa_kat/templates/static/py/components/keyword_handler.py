#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import window
from browser import document


# Functions & classes =========================================================
class KeywordListHandler(object):
    """
    This class is used to control the GUI for the list of keywords.

    It allows user to add new keyword, remove present keyword and get a list
    of defined keywords.
    """
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
        """
        Render the HTML code for all the :attr:`keywords` stored in this class.

        This method is called after each change in :attr:`keywords`.
        """
        # hide the list in case that there is no `keyword` to be displayed
        if cls.keywords:
            cls.whole_el.style.display = "block"
        else:
            cls.whole_el.style.display = "none"

        # construct the HTML code for each keyword
        html_lines = (
            "<li class='kw_enum'>{0} {1}</li>\n".format(
                keyword,
                (cls._remover % cnt)
            )
            for cnt, keyword in enumerate(cls.keywords)
        )

        # put the keywords into the HTML code of the page
        cls.div_el.innerHTML = "<ol>\n%s\n</ol>\n" % "\n".join(html_lines)

        # this function is used to bind the ✖ to function for removing the
        # keyword
        def keyword_remover(keyword):
            def remover(ev):
                cls.remove_keyword(keyword)

            return remover

        # go thru all the keywords and bind them to keyword_remover()
        for cnt, keyword in enumerate(cls.keywords):
            uid = "kw_remover_id_%d" % cnt
            el = document[uid]
            el.bind("click", keyword_remover(keyword))

    @classmethod
    def add_keyword(cls, keyword):
        """
        Add `keyword` to :attr:`keywords`.

        Args:
            keyword (str): New keyword.
        """
        cls.keywords.append(keyword)
        cls._render()

    @classmethod
    def remove_keyword(cls, keyword):
        """
        Remove `keyword` from :attr:`keywords`.

        Args:
            keyword (str): Keyword which should be removed.
        """
        cls.keywords.remove(keyword)
        cls._render()


class KeywordAdder(object):
    """
    This class is here to controll typeahead input bar with keyword suggestion.

    Keywords selected from suggestions are then mapped to
    :class:`KeywordListHandler`.
    """
    intput_el = document["keyword_adder"]

    @classmethod
    def on_select_callback(cls, selected_item):
        """
        This method defines the action taken when user selects the keyword from
        suggestion engine.

        Args:
            selected_item (str): Keyword selected by the user.

        Returns:
            str: Value on which the <input> element will be set.
        """
        KeywordListHandler.add_keyword(selected_item)

        return ""

    @classmethod
    def set_kw_typeahead_input(cls):
        """
        Map the typeahead input to remote dataset.
        """
        # get reference to parent element
        parent_id = cls.intput_el.parent.id
        if "typeahead" not in parent_id.lower():
            parent_id = cls.intput_el.parent.parent.id

        window.make_keyword_typeahead_tag(
            "#" + parent_id,
            "/api_v1/kw_list.json",
            cls.on_select_callback,
        )

KeywordAdder.set_kw_typeahead_input()
