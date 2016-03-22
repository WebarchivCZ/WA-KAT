Uživatelská a administrátorská dokumentace projektu WA-KAT
==========================================================

Systém WA-KAT je nástroj soužící pro semi-automatickou katalogizaci a klasifikaci webových zdrojů.

Aplikace obsahuje rozhraní pro tvorbu katalogizačních záznamů nestrukturovaných elektronicých zdrojů, včetně možnosti definovat pravidla a katalogizovat zdroje podle pravidel sklízecí aplikace, které určují hloubku, restrikce a technické odchylky při sklízení stránek.

Součástí zadání projektu bylo:

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

Součástí zadání také byla specifikace projektu jako samostatné webové aplikace, které má návaznost na další systémy používané v Národní knihovně. Aplikace je vývíjena jako open-source pod licencí MIT, zdrojové kódy jsou dostupné na platformě GitHub.

Uživatelská dokumentace
-----------------------
Z pohledu uživatele je aplikace reprezentována jednou dynamickou webstránkou, která umožňuje provádět analýzy zadané URL. Dále umožňuje načíst některé informace ze systému Aleph na základě zadaného ISSN, pokud takový záznam již v bázi NTK existuje.

Pokud je aplikace otevřena ze systému Seeder, WA-KAT umí stáhnout některé relevantní informace z jeho databáze a předvyplnit je do formulářů.

Webová aplikace provádí dynamické validace zadaných dat. Další funkcí je vyhledání konkrétního autora v autoritní bázi NK. Posledním krokem je generování záznamu ve formátu MRC používaném v desktopové aplikaci Aleph, dále pak v XML formátu MARC, který je používaný backendovou a webovou částí systému Aleph a také ve formátu Dublin core, který je mezinárodním formátem pro přenos a uchovávání metadat.

Jednotlivé komponenty
+++++++++++++++++++++

URL
^^^

První komponentou na stránce je pole pro zadání adresy `URL`. Adresa může být zadána s ``http://``, či ``https://``. Pokud toto není zadáno chybí, automaticky je doplněn prefix ``http://``.

Odeslání tohoto formuláře je možné kliknutím na tlačítko `Spustit`, či stisknutím klávesy ENTER.

Jelikož analýzy probíhají delší dobu (podle webu cca 20 vteřin), zobrazuje se pod polem `URL` aktivní `progress bar` zobrazující uživateli informaci o postupujících analýzách. `Progress bar` je postupně aktualizován v cca osmi krocích.

ISSN
^^^^

Pod polem `URL` následuje pole pro zadání `ISSN`.

Administrátorská dokumentace
----------------------------

Zdrojové kódy
+++++++++++++

Instalace
+++++++++

TODO: Zmínit scripty co to nainstaluje do systémových cest.

Nasazení a spuštění
+++++++++++++++++++

wa_kat_server.py
^^^^^^^^^^^^^^^^

Konfigurace
+++++++++++

Popis architektury systému
++++++++++++++++++++++++++

Zadání projektu jakožto webové aplikace si vyžádalo rozdělení aplikační logiky do komponent backendu, a frontendu. Díky použítí JavaScriptového Python interpretru Brython bylo možné zachovat jednotnost jazyka v rámci obou částí projektu

Backend
^^^^^^^

Frontend
^^^^^^^^

REST API
--------
