.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3


Fiskalizacija računa
=====================

Fiskalizacija računa po zakonskoj regulativi u Republici Hrvatskoj

Na qweb ispis računa dodaje polja JIR i ZKI iznad polja komentar.
TODO: opcija ispisa: u jdnom redu ili u dva, config na company

Setup
-----

Postavke -> Kriptografija -> Certifikati

   - učitati certifikat, pretvoriti ga u PEM i potvrditi

Tvrtke -> <TVRTKA> -> Uredi
   kartica Croatia specific data
   - Odabrati certifikat za fiskalizaciju
   - poslovni prostori i naplatni uređaji
      ->dopun dopuniti podatke o adresi, i prijaviti prostor u PU

Računovodstvo -> Postava -> Računovodstvo -> Porezi
  - svi porezi prodaje trebaju imati postavljen ispravan fiskalni tip poreza


Računovodstvo -> Postava -> Računovodstvo ->Dnevnici ->
   - Kartica Specifičnosti za HR lokalizaciju
      Moguće aktivirati fiskalizaciju za odabrani dnevnik

KORISNE INFORMACIJE :

- https://marker.hr/blog/web-shop-fiskalizacija-254/
- http://www.porezna-uprava.hr/HR_publikacije/Lists/mislenje33/Display.aspx?id=19173

Usage
-----

Nothing special, setup is important!

TODO:
-----



Bug Tracker
===========


In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback

Credits
=======

Contributors
------------

- Davor Bojkić <davor.bojkic@storm.hr>
- Goran Kliska <goran.kliska@slobodni-programi.hr>
- Boris Tomić <boris@kodmasin.net>  / FiskPy SMOP-ed

Icon
----




Maintainer
----------


