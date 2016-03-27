WA-KAT documentation
====================

WA-KAT is a project that simplifies the job of curators of the Webarchive of National Library of the Czech Republic by cataloging electronic resources using semi-automatic analysis.

Project is written in Python as single page `bottle.py <http://bottlepy.org>`_ application.

User manual
-----------

    - :doc:`manual`

Component documentation
-----------------------

Here is `programmer` documentation of all components.

:doc:`/api/wa_kat`:

.. toctree::
    :maxdepth: 1

    /api/data_model.rst
    /api/settings.rst

:doc:`/api/analyzers/analyzers`:

.. toctree::
    :maxdepth: 1

    /api/analyzers/author_detector.rst
    /api/analyzers/annotation_detector.rst
    /api/analyzers/creation_date_detector.rst
    /api/analyzers/keyword_detector.rst
    /api/analyzers/language_detector.rst
    /api/analyzers/place_detector.rst
    /api/analyzers/title_detector.rst

.. toctree::
    :maxdepth: 1

    /api/analyzers/source_string.rst

.. toctree::
    :maxdepth: 1

    /api/analyzers/shared.rst

:doc:`/api/connectors/connectors`:

.. toctree::
    :maxdepth: 1

    /api/connectors/aleph.rst
    /api/connectors/seeder.rst

:doc:`/api/convertors/convertors`:

.. toctree::
    :maxdepth: 1

    /api/convertors/mrc.rst
    /api/convertors/to_dc.rst
    /api/convertors/iso_codes.rst

:doc:`/api/rest_api/rest_api`:

.. toctree::
    :maxdepth: 1

    /api/rest_api/bottle_index.rst
    /api/rest_api/keywords.rst
    /api/rest_api/analyzers_api.rst
    /api/rest_api/aleph_api.rst
    /api/rest_api/virtual_fs.rst
    /api/rest_api/to_output.rst

.. toctree::
    :maxdepth: 1

    /api/rest_api/shared.rst

:doc:`/api/zeo/zeo`:

.. toctree::
    :maxdepth: 1

    /api/zeo/request_info.rst
    /api/zeo/request_database.rst

.. toctree::
    :maxdepth: 1

    /api/zeo/worker.rst

Source code
-----------
This project is released as opensource (MIT) and source codes can be found at
GitHub:

- https://github.com/WebArchivCZ/WA-KAT


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
