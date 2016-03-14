#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from setuptools import setup
from setuptools import find_packages

from docs import getVersion


# Variables ===================================================================
CHANGELOG = open('CHANGELOG.rst').read()
LONG_DESCRIPTION = "\n\n".join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    CHANGELOG
])


# Actual setup definition =====================================================
setup(
    name='wa-kat',
    version=getVersion(CHANGELOG),
    description="Web page analyzator for czech webarchive.",
    long_description=LONG_DESCRIPTION,
    url='https://github.com/WebArchivCZ/WA-KAT',

    author='Bystroushaak',
    author_email='bystrousak[at]kitakitsune.org',

    classifiers=[
        "Development Status :: 3 - Alpha",

        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: MIT License",
    ],
    license='MIT',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    include_package_data=True,
    zip_safe=False,

    scripts=[
        "bin/wa_kat_server.py",
        "bin/wa_kat_mrc_to_xml.py",
        "bin/wa_kat_build_conspects.py",
        "bin/wa_kat_build_keyword_index.py",
    ],

    install_requires=open("requirements.txt").read().splitlines(),
    extras_require={
        "test": [
            "pytest",
        ],
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
        ]
    }
)
