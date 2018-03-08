.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3


Kontni plan RRIF 2015 - Porez po naplaćenoj naknadi
===================================================

This is the extension module to manage the accounting chart for Croatia tax vat on payment

- RRIF 2015 kontni plan dopuna poreza i poreznih grupa za obračun poreza prema naplaćenom:

- modul dodaje:
  - dnevnik Evidencije poreza prema naplaćenom (nije vidljiv na ndzornoj ploči)
  - kreira brojevni krug za dnevnik
  - kreira dodatne poreze ( po napl.)
  - postavi kreirani dnevnik poreza prema naplaćenom u postavkama računovodstva
  - dopuni fiskalne pozicije sa novim porezima

- Modul se instalira automatski ako je prethodno installiran modul l10n_hr_coa_rrif_2015
   a uključi se opcija 'Omogući poreze po naplaćenom' na postavkama poduzeća
    (instalira se modul: account_tax_cash_basis)




Usage
=====

Nakon instalacije potrebno je dodatno provjeriti postavke zadanih poreza u prodaji i nabavi
kako bi se primjenjivao ispravan porez. Ukoliko želite možete stare poreze obrisati,
ali preporučljivo je samo ih deaktivirati.
(PDV i PPDV 25,13 i 5 % za koje su kreirani ekvivalentni parovi po napl.)


Contributors
------------

Davor Bojkić - Daj Mi 5 - bole (at) dajmi5.com


