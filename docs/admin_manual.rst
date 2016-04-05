Administrátorská dokumentace projektu WA-KAT
=============================================

V následující části je popsána architektura, umístění zdrojových kódů, instalace, konfigurace a správa projektu.


Architektura systému
--------------------

Zadání projektu jakožto webové aplikace si vyžádalo rozdělení aplikační logiky do komponent backendu a frontendu.

Díky použítí Python interpretru Brython napsaném v JavaScriptu bylo možné zachovat jednotnost jazyka v rámci obou částí projektu, i když na backendu je z důvodu zpětné kompatibility s knihovnami použit Python 2.7 a na frontendu Python 3.


Backend
+++++++
Backend je koncipován jako aplikace napsaná ve frameworku Bottle_.

.. _Bottle: http://bottlepy.org/

Zdrojové kódy je možné nalézt ve složce `src/wa_kat <https://github.com/WebArchivCZ/WA-KAT/tree/master/src/wa_kat>`_.


Frontend
++++++++

Zdrojové kódy je možné nalézt ve složce `src/wa_kat/templates/static/js/Lib/site-packages/ <https://github.com/WebArchivCZ/WA-KAT/tree/master/src/wa_kat/templates/static/js/Lib/site-packages>`_.


Zdrojové kódy projektu
----------------------
Zdrojové kódy jsou umístěny na serveru GitHub:

    - https://github.com/WebArchivCZ/WA-KAT/

Kódy jsou uvolněny a volně přístupné pod OpenSource licencí MIT.


Instalace
---------
Ačkoliv nic nebrání provozování projektu pod alternativními operačními systémy, projekt WA-KAT je od začátku koncipován jako program běžící v prostředí Linux. Testování a vývoj probíhal na Linuxové distribuci ``Ubuntu server 14.04``.

Instalaci je možné provést pomocí standardního pythonního instalátoru `PIP <https://pip.pypa.io>`_. Ten by měl být automaticky přítomen ve většině linuxových distribucí.

Pokud není, či je v příliš staré verzi, je možné ho nainstalovat pomocí pokynů `uvedených v dokumentaci <https://pip.pypa.io/en/stable/installing/>`_, či instalací z package manageru distribuce (balík ``python-pip``).

Dále je nutné se ujistit, že instalátor má všechny potřebné nástroje pro kompilování zdrojových kódů knihoven a závislostí. Tyto nástroje jsou většinou dostupné ve správci balíků konkrétní distribuce pod názvem ``python-dev`` či ``python-devel``.

V případě Ubuntu / ``deb`` systémů je možné nainstalovat potřebné moduly příkazem::

    sudo apt-get install python-dev

Na systémech openSuse lze použít příkaz::

    sudo zypper install python-devel

Poté je již možno nainstalovat přímo WA-KAT příkazem::

    sudo pip install -U wa-kat

Posledním krokem, který je nutné provést je inicializace korpusu textového tokenizeru příkazem::

    python -m textblob.download_corpora


Nainstalované scripty
+++++++++++++++++++++
Správně provedná instalace by měla do systémových cest nainstalovat následující scripty:

    - ``wa_kat_server.py``
    - ``wa_kat_build_conspects.py``
    - ``wa_kat_build_keyword_index.py``

Ověření je možné provést například příkazem::

    which wa_kat_server.py

Což by mělo vypsat řádek podobný tomuto::

    /usr/local/bin/wa_kat_server.py


wa_kat_server.py
^^^^^^^^^^^^^^^^
Tento script slouží pro běh samotného Bottle serveru, jedná se tedy o hlavní script celého prokejtu.

Script nepřijímá žádné parametry. Po spuštění vypíše hlášení::

    Waiting for ZEO connection..

a čeká, dokud není zpřístupněno spojení na databázi. Jakmile je spojení navázáno, zobrazí informaci o URL, kde běží a dále pokračuje zobrazováním přístupového logu::

    Bottle v0.12.9 server starting up (using PasteServer())...
    Listening on http://localhost:8080/
    Hit Ctrl-C to quit.

    serving on http://127.0.0.1:8080

Nápověda::

    $ bin/wa_kat_server.py -h
    usage: wa_kat_server.py [-h]

    WA-KAT server runner.

    optional arguments:
      -h, --help  show this help message and exit


wa_kat_build_keyword_index.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Jak už název napovídá, tento script slouží k sestavení indexu všech klíčových slov (`předmětových hesel`).

Script umožňuje fungovat ve dvou módech:

    #) Stáhnutí indexu záznamů z Alephu.
    #) Generování souboru s indexem ze stažených záznamů (přepínač ``-g``).

Výsledným souborem je poté možno nahradit starý index umístěný v `/src/wa_kat/templates/keyword_list.json.bz2 <https://github.com/WebArchivCZ/WA-KAT/blob/master/src/wa_kat/templates/keyword_list.json.bz2>`_.

Nápověda::

    $ bin/wa_kat_build_keyword_index.py -h
    usage: wa_kat_build_keyword_index.py [-h] [-c CACHE] [-o OUTPUT] [-s N] [-g]

    Aleph keyword index builder. This program may be used to build fast index for
    the keywords from AUT base.

    optional arguments:
      -h, --help            show this help message and exit
      -c CACHE, --cache CACHE
                            Name of the cache file. Default
                            `./aleph_kw_index.sqlite`.
      -o OUTPUT, --output OUTPUT
                            Name of the output file. Default
                            `./keyword_list.json`.
      -s N, --start-at N    Start from N instead of last used value.
      -g, --generate        Don't download, only generate data from dataset.


wa_kat_build_conspects.py
^^^^^^^^^^^^^^^^^^^^^^^^^
Dalším scriptem je nástroj, který ze zadaného setu záznamů (je možné na požádání získat od správců Alephu v NK) sestaví index Konspektů a Subkonspektů se správnými hodnotami MDT a DDC.

Nápověda::

    usage: wa_kat_build_conspects.py [-h] XML_FILE

    This program may be used to convert Conspectus / Subconspectus set in MARC XML
    to JSON.

    positional arguments:
      XML_FILE    MARC XML file packed in .bz2.

    optional arguments:
      -h, --help  show this help message and exit


runzeo
^^^^^^
Poslední program `runzeo` není přímou součástí projektu WA-KAT, je však součástí jeho distribuce, jelikož je nainstalován jako jedna ze závislostí.

Tento program slouží k provozu objektové databáze ZODB formou ZEO clusteru. Typické spuštění vypadá následovně::

    runzeo -C conf/zeo.conf

Podrobnosti viz následující sekce.



První spuštění a provoz
-----------------------

Pro běh projektu je nutné zajistit trvalé spuštění dvou procesů:

    - ``wa_kat_server.py``
    - runzeo -C conf/zeo.conf  TODO: !

První zajišťuje běh webové aplikace, druhý pak provoz databáze.

Tyto příkazy je možné pro otestování spustit ručně ve dvou samostatných konzolích, pro produkční nasazení ovšem doporučuji přidat scripty do systému Supervisor.


Supervisor
++++++++++

Program `Supervisor <http://supervisord.org/>`_ slouží ke správě a automatickému spouštění aplikací jako unixových daemonů. Tento program může administrátorům ušetřit spoustu práce s konfigurací služeb pro běh jako pravý daemon (odpojené tty, reakce na signály, logy..).

Supervisor je možné nainstalovat pomocí balíčkovacího systému distribuce::

    sudo apt-get install supervisor


Manuální instalace
^^^^^^^^^^^^^^^^^^

V případě, že používáte distribuci, která Supervisor v balíčkovacím systému neobsahuje, je možné ho nainstalovat manuálně v několika krocích.

Samotnou binárku nainstalujeme přes PIP::

    sudo pip install supervisor

Dále je nutné vytvořit defaultní konfigurační soubor::

    mkdir /etc/supervisor
    echo_supervisord_conf > /etc/supervisor/supervisord.conf

Dalším nutným krokem je vytvoření patřičného runlevel souboru, který zajistí spuštění Supervisoru po každém restartu. Init scripty je možné najít na githubu:

    - https://github.com/Supervisor/initscripts

V případě ubuntu je možné použít následující příkazy::

    sudo su
    curl https://raw.githubusercontent.com/Supervisor/initscripts/fc840d1684bba74c6c6c9a1fe48bd48d07c2b25b/ubuntu > /etc/init.d/supervisord
    chmod +x /etc/init.d/supervisord
    update-rc.d supervisord defaults


Konfigurace pro WA-KAT
^^^^^^^^^^^^^^^^^^^^^^
Konfiguraci pro WA-KAT provedeme přidáním následujících řádek do konfiguračního souboru (``/etc/supervisord.conf`` či ``/etc/supervisor/supervisord.conf``, podle distribuce)::





Konfigurace WA-KATu
-------------------

Konfigurace pomocí ENV proměnné.



REST API
--------



Uživatelská dokumentace
-----------------------


Pro větší přehlednost byla přesunuta do samostatného souboru:

    - :doc:`manual`
