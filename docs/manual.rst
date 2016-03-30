Uživatelská a administrátorská dokumentace projektu WA-KAT
==========================================================

Systém WA-KAT je nástroj soužící pro semi-automatickou katalogizaci a klasifikaci webových zdrojů.

Aplikace obsahuje rozhraní pro tvorbu katalogizačních záznamů nestrukturovaných elektronicých zdrojů, včetně možnosti definovat pravidla a katalogizovat zdroje podle pravidel sklízecí aplikace, které určují hloubku, restrikce a technické odchylky při sklízení stránek.

Zadáním projektu mimo jiné bylo:

    - propojení se systémy ALEPH (báze NK, ISSN NTK)
    - extrakce textu z webových zdrojů a jejich analýza pro vytváření klíčových slov
    - extrakce metadat a jejich kategorizace
    - automatické určení stáří stránky (napojení na registry WHOIS, IA)
    - určení jazyku webové stránky
    - možnost určit z předdefinovaných parametrů pravidla pro sklízení
    - ze zadaných údajů vytvoření validního katalogizačního záznamu a jeho export do formátů MARCXML, XML (DC) a databáze kurátorského systému
    - propojení se systémem Seeder
    - rozhraní pro ruční zadání dalších potřebných údajů
    - vytvoření API, které umožní pristupovat k jednotlivým funkcím samostatně

Součástí zadání také byla specifikace projektu jako samostatné webové aplikace, preferovaně v jazyce Python, a také návaznost na další systémy používané v Národní knihovně.

Aplikace je vývíjena jako open-source pod licencí MIT, zdrojové kódy jsou dostupné na platformě GitHub.



Uživatelská dokumentace
-----------------------
Z pohledu uživatele je aplikace reprezentována jednou dynamickou webstránkou, která umožňuje provádět analýzy zadané URL. Dále umožňuje načíst některé informace ze systému Aleph na základě zadaného ISSN, pokud takový záznam již v bázi NTK existuje. Ostatní informace je možné ručně doplnit.

.. image:: /images/wa_kat.png
    :width: 600px

Pokud je aplikace otevřena ze systému Seeder, WA-KAT umí stáhnout některé relevantní informace z jeho databáze a předvyplnit je do formulářů. Další funkcí je vyhledání konkrétního autora v autoritní bázi NK.

Webová aplikace provádí dynamické validace vyplnění dat. Posledním krokem je generování záznamu ve formátu MRC používaném v desktopové aplikaci Aleph, dále pak v XML formátu MARC, který je používaný backendovou a webovou částí systému Aleph a také ve formátu Dublin core, který je mezinárodním formátem pro přenos a uchovávání metadat.



Jednotlivé komponenty
+++++++++++++++++++++

Každá z komponent obsahuje nápovědu v podobě otazníku vedle popisku. V případě, že uživatel na otazník klikne, je mu zobrazena tato nápověda.

Následuje popis všech uživatelem ovlivnitelných elementů:

URL
^^^

První komponentou na stránce je pole pro zadání adresy `URL`. Adresa může být zadána s ``http://``, či ``https://``. Pokud toto není zadáno, automaticky je doplněn prefix ``http://``.

V případě, že uživatel zadá do pole `URL` identifikátor `ISSN`, aplikace ho automaticky rozpozná a přemístí do patřičného pole, načež dojde ke spuštění požadavku na dohledání katalogizačního záznamu k tomuto ISSN.

Na pravé straně pole pro zadání `URL` se nachází tlačítko `Spustit`. Jak název napovídá, stisknutím tlačítka je spuštěna analýza zadané adresy. Alternativní možností je stisknutí klávesy ENTER.

Jelikož analýzy probíhají delší dobu (podle složitosti stránek cca 20 vteřin), zobrazuje se pod polem `URL` aktivní `progress bar` zobrazující uživateli informaci o postupujících analýzách. `Progress bar` je postupně aktualizován v cca osmi krocích.

.. image:: /images/url_progressbar.png
    :width: 600px


V případech, kdy není možné načíst webovou stránku je zobrazena chybová hláška a tento fakt je zaznamenán do interního logu:

.. image:: /images/url_error.png
    :width: 600px

Popisek pole `URL` úplně vlevo je červeně podtržený, pro zdůraznění nutnosti vyplnit toto pole. V případě, že uživatel pole nevyplní mu nebude dovoleno odeslat formulář a celé pole pro zadání informace bude zvýrazněno. Pod polem je zobrazeno vysvětlující chybové hlášení (v množném čísle, neboť se nevztahuje pouze k poli `URL`, ale ke všem nevyplněným):

.. image:: /images/url_validation.png
    :width: 600px

ISSN
^^^^

Pod polem `URL` následuje pole pro zadání `ISSN`_ - `mezinárodního standardního čísla seriálové publikace`. Tímto formulářem je možné načíst informace z `báze ISSN`_ Národní technické knihovny. Zde je v některých případech částečný záznam periodika, který je použit pro vyplnění některých z níže uvedených polí.

.. _ISSN: https://cs.wikipedia.org/wiki/International_Standard_Serial_Number
.. _báze ISSN: https://aleph.techlib.cz/F/?func=find-b-0&local_base=stk02

.. image:: /images/issn.png
    :width: 600px

Načítání dat je indikováno `progressbarem`:

.. image:: /images/issn_progressbar.png
    :width: 600px

Formulář je stejně jako v předchozím případě možné spustit buďto kliknutím na tlačítko `Načíst`, či stisknutím klávesy ENTER. V případě chyby je zobrazeno varovné hlášení:

.. image:: /images/issn_error.png
    :width: 600px

Pole ISSN je nepovinné.

Název
^^^^^

Název je možné buďto vyplnit ručně, či nechat načíst z analýz, či z báze ISSN. V případě analýz je vyhledáván v:

    - HTML tagu ``<title>``
    - HTML meta tagu ``<meta name="title" content="..">``
    - HTML Dublin core tagu ``<meta name="DC.Title" content="..">``

Existuje tedy pět možností zdroje dat. Widget (nejenom pro ISSN, ale i všechny následující inputy, pokud není řečeno jinak) s těmito možnostmi počítá a upravuje jim svůj vzhled.

Pro ruční zadání se chová jako standardní HTML input:

.. image:: /images/title.png
    :width: 600px

V případě načtení z báze ISSN národní knihovny zobrazí na pravé straně ikonu oka, která má upozornit uživatele na fakt, že se jedná o načtenou hodnotu. Vedle ikony oka se poté nachází zdroj informace, v tomto případě se jedná o systém `Aleph`.

.. image:: /images/title_aleph.png
    :width: 600px

Poslední možností je vstup dat z `analýz`. Jelikož se jedná o tři potenciální pod-zdroje dat (HTML, meta a DC), existují dvě podvarianty chování widgetu:

V případě, kdy analýzy nalezly jednu hodnotu bude widget vypadat stejně jako v případě ISSN, tedy ikona oka, vedle které se nachází informace o zdroji:

.. image:: /images/title_analysis.png
    :width: 600px

V případě, že je nalezených možností více, zobrazí se místo ikony oka šipka nabízející výběr dalších hodnot. Input samotný bude prázdný, ale popisek na pozadí obsahuje informaci o možnosti výběru:

.. image:: /images/title_analysis_choice.png
    :width: 600px

Po kliknutí se pak zobrazí nabídka nalezených hodnot, kde na levé straně se nachází zdroj informace:

.. image:: /images/title_analysis_dropdown.png
    :width: 600px

Po výběru je možné hodnotu nadále upravovat jako textový vstup:

.. image:: /images/title_analysis_choice_edit.png
    :width: 600px

Pole `Název` je povinné.

Podnázev
^^^^^^^^

`Podnázev` může být kurátory vyplněn ručně, či doplněn automaticky načtením dat z báze ISSN.28.03.2016

.. image:: /images/subtitle.png
    :width: 600px

Pole `Podnázev` je nepovinné.

Datum vzniku
^^^^^^^^^^^^

`Datum vzniku` webu je v současné verzi vyhledáváno v registru Whois a kontrolou přítomnosti archivních záznamů ve Webarchivu prostřednictvím webu `mementoweb.com`_, který sleduje a prostřednictvím jednotného API zpřístupňuje `mnoho registrů`_.

.. _mementoweb.com: http://timetravel.mementoweb.org/
.. _mnoho registrů: http://timetravel.mementoweb.org/about/

.. image:: /images/creation_date.png
    :width: 600px

Pokud není hodnota nalezena, je pole na žádost kurátorů, kteří systém WA-KAT používají, předvyplněna hodnotou ``[XXXX?]-``, což je konvence používaná v MRC / MARC záznamech.

`Datum vzniku` může být doplněn načtením dat z báze ISSN.

Očekávaným vstupem pro `Datum vzniku` je **rok**, případně rozsah let::

    2009
    2009-
    2009-2015

Knihovnické konvence formátu MARC však dovolují různé reprezentace, program proto data do některých polí přenáší tak, jak jsou zadána a v jiných (specificky ``008``) provádí extrakce let a přenáší pouze číselnou hodnotu.

Pole `Datum vzniku` je povinné.

Vydavatel
^^^^^^^^^

`Vydavatel` slouží k zadání volně psaného názvu vydavatele stránek. Vydavatelem je obvykle myšlena osoba, která se stará o publikaci, či zajišťuje hosting.

.. image:: /images/publisher.png
    :width: 600px

Na poli `Vydavatel` na první pohled zaujme `checkbox`, mezi popiskem pole a prostorem pro zadání hodnoty. Zašktnutím tohoto `checkboxu` je možné odkrýt dialog pro výběr `Autora` (viz dále).

`Vydavatel` je analyzátory vyhledáván v:

    - HTML meta tagu ``<meta name="author" content="..">``
    - HTML Dublin core tagu ``<meta name="DC.Creator" content="..">``

`Vydavatel` také může být doplněn načtením dat z báze ISSN.

Pole `Vydavatel` je povinné.

Autor
^^^^^

V případě zaškrnutí `checkboxu` vedle pole `Vydavatel` se zobrazí dialog pro výběr autora:

.. image:: /images/author.png
    :width: 600px

`Autorem` se v tomto případě chápe tvůrce obsahu webu, se kterým je sjednána smlouva u uložení do databází webarchivu. Jedná se tudíž vždy pouze o entitu uvedenou v `Autoritní bázi`_ Národní knihovny. Díky tomu se nejedná o volně vyplnitelné vstupní pole.

.. _Autoritní bázi: http://aleph.nkp.cz/F/?func=file&file_name=find-b&local_base=AUT

Kliknutím na tlačítko vybrat se zobrazí dialog pro vyhledání autora v autoritní bázi:

.. image:: /images/author_picker.png
    :width: 400px

Vyhledání je možné po napsání názvu spustit buďto klávesou ENTER, či stisknutím tlačítka `Vyhledat`, po němž dojde k dotázání autoritní báze a zobrazení nalezených výsledků:

.. image:: /images/author_picker_choices.png
    :width: 400px

Z nich je možné označit a vybrat konkrétního autora.

.. image:: /images/author_chosen.png
    :width: 600px

`Autor` také může být doplněn načtením dat z báze ISSN.

Pole `Autor` je nepovinné.

Místo
^^^^^

`Místem` je chápáno nejčastěji město, kde jsou webstránky hostovány, může se ale také jednat o sídlo `Vydavatele`, či `Autora`.

.. image:: /images/place.png
    :width: 600px

`Místo` je analyzátory vyhledáváno v:

    - HTML Dublin core tagu ``<meta name="geo.placename" content="..">``
    - Registru Whois

`Místo` může být doplněno načtením dat z báze ISSN.

Pole `Místo` je nepovinné.

Předmětová hesla
^^^^^^^^^^^^^^^^
TODO: Nezapomenout zmínit změnu popisku po přidání alespoň jednoho hesla.

Konspekt / Subkonspekt
^^^^^^^^^^^^^^^^^^^^^^

TODO: Nezapomenout zmínit přepínátko.

Jazyk
^^^^^

Anotace
^^^^^^^

TODO: Nezapomenout zmínit ignoraci komentářů.

Periodicita
^^^^^^^^^^^

Frekvence sklízení
^^^^^^^^^^^^^^^^^^

Pravidla
^^^^^^^^


Tlačítka
^^^^^^^^

Vyčistit
~~~~~~~~


Generovat MARC
~~~~~~~~~~~~~~


Skrytý log
^^^^^^^^^^





Administrátorská dokumentace
----------------------------

Zdrojové kódy
+++++++++++++

Instalace
+++++++++

python -m textblob.download_corpora

TODO: Zmínit scripty co to nainstaluje do systémových cest.

Nasazení a spuštění
+++++++++++++++++++

wa_kat_server.py
^^^^^^^^^^^^^^^^

Konfigurace
+++++++++++

Konfigurace pomocí ENV proměnné.

Popis architektury systému
++++++++++++++++++++++++++

Zadání projektu jakožto webové aplikace si vyžádalo rozdělení aplikační logiky do komponent backendu, a frontendu. Díky použítí JavaScriptového Python interpretru Brython bylo možné zachovat jednotnost jazyka v rámci obou částí projektu

Backend
^^^^^^^

Frontend
^^^^^^^^

REST API
--------
