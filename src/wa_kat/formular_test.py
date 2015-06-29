#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from formular import HTMLForm
from formular import TextField
from formular import PasswordField


# Variables ===================================================================
# Functions & classes =========================================================
class LoginForm(HTMLForm):
    username = TextField(label=u"Username", required=True)
    password = PasswordField(label=u"Password", required=True)
    repeat_password = password.copy(label=u"Repeat Password", equals="password")


# Main program ================================================================
if __name__ == '__main__':
    lf = LoginForm()

    print lf.as_widget()
