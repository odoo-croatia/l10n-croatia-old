.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Računovodstvo - Hrvatska  lokalizacija
======================================

Croatian localisation. Accounting

- base accounting fields




1. Setup
----------------


- prema zakonu o fiskalizaciji, potrebno je dofinirati poslovne prostore i naplatne uređaje.
Izbornik: Računovodstvo -> Postava -> Hrvatska - postavke
   - ovi podaci služe za generiranje broja računa u skladu sa zakonom o fiskalizaciji,
     prefiks i sufix na brojevnim krugovima služe samo za interni broj računa u sustavu


2. Journal setup
----------------
Na dnevnicima izlaznih računa potrebno je odrediti:

- zadani naplatni uređaj, (i dozvoljene naplatne uređaje),
- usere koji imaju pravo knjiženja u dnevnik

3. User setup
-------------
Korisnicima je potrebno omogućiti izdavanje računa na postavkama korisnika,
Dodijelite im prvo prava da izdau račune u određenim poslovnim prostorima,
pa potom i dodjelite koje uređaje smiju koristiti


TODO:
dodati configuraciju za gomilu kontrola uključiti po željama (user/grupa)



