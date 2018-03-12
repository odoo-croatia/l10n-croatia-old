# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from .. import fisk
import datetime


class FiscalInvoiceMixin(models.AbstractModel):
    _name = "fiscal.invoice.mixin"


    vrijeme_xml = fields.Char(
        string="XML vrijeme računa",
        help="Value from fiscalization msg stored as string",
        size=19, readonly=True, copy=False)
    fiskal_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Fiskalizirao',
        help='Fiskalizacija. Osoba koja je potvrdila racun',
        copy=False)
    zki = fields.Char(
        string='ZKI',
        readonly=True, copy=False)
    jir = fields.Char(
        string='JIR',
        readonly=True, copy=False)
    paragon_br_rac = fields.Char(
        'Paragon br.',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Paragon broj racuna, ako je racun izdan na paragon.")

    @api.one
    def _fiskal_invoice_valid(self):
        if not self.journal_id.fiscal_active:
            raise UserError(
                _('Za ovaj dokument fiskalizacija nije aktivna!!'))
        if not self.fiskal_user_id.partner_id.vat:
            raise UserError(
                _('Neispravan ili nije unešen OIB korisnika!'))
        if not self.company_id.fiskal_cert_id:
            raise MissingError(
                _('No fiscal certificate found, please install one or select it as active on company setup!'))
        return True

    def _fiskal_num2str(self, num):
        return "{:-.2f}".format(num)

    #@api.one  DB: without descriptor!!! othervise returns list!
    def _prepare_fisk_racun_taxes(self):
        tax_data = {
            "Pdv": [],
            "Pnp": [],
            "OstaliPor": [],
            "Naknade": [],
        }
        iznos_oslob_pdv = iznos_ne_podl_opor = iznos_marza = 0.00
        for tax in self.tax_line_ids:
            # TODO: special cases with sub taxes?
            if not tax.tax_id.hr_fiskal_type:
                raise ValidationError(_("Tax '%s' missing fiskal type!" % tax.tax_id.name))
            else:
                fiskal_type = str(tax.tax_id.hr_fiskal_type)
            #tax_code = tax.tax_code_id
            naziv = str(tax.tax_id.name) # DB: do i need this name here and for what???
            stopa = self._fiskal_num2str(tax.tax_id.amount)
            osnovica = self._fiskal_num2str(tax.base)
            iznos = self._fiskal_num2str(tax.amount)
            if fiskal_type == 'pdv':
                tax_data['Pdv'].append(fisk.Porez({
                    "Stopa": stopa, "Osnovica": osnovica, "Iznos": iznos}))
            elif fiskal_type == 'pnp':
                tax_data['Pnp'].append(fisk.Porez({
                    "Stopa": stopa, "Osnovica": osnovica, "Iznos": iznos}))
            elif fiskal_type == 'ostali':
                tax_data['OstaliPor'].append(fisk.OstPorez({
                    "Naziv": naziv,
                    "Stopa": stopa, "Osnovica": osnovica, "Iznos": iznos}))
            elif fiskal_type == 'naknade':
                tax_data['Naknade'].append(fisk.Naknada({
                    "NazivN": naziv, "IznosN": iznos}))

            elif fiskal_type == 'oslobodenje':
                iznos_oslob_pdv += tax.base
            elif fiskal_type == 'ne_podlijeze':
                iznos_ne_podl_opor += tax.base
            elif fiskal_type == 'marza':
                iznos_marza += tax.base

        for l in ["Pdv", "Pnp", "OstaliPor", "Naknade"]:
            if not tax_data[l]:
                del tax_data[l]
        if iznos_oslob_pdv:
            tax_data['IznosOslobPdv'] = self._fiskal_num2str(iznos_oslob_pdv)
        if iznos_ne_podl_opor:
            tax_data['IznosNePodlOpor'] = self._fiskal_num2str(iznos_ne_podl_opor)
        if iznos_marza:
            tax_data['IznosMarza'] = self._fiskal_num2str(iznos_marza)

        # TODO group and sum by fiskal_type and Stopa hmmm
        # then send 1 by one into factory...
        return tax_data

    def _prepare_fisk_racun(self, production, time_start):
        # 1. get company OIB
        if production:
            oib = self.company_id.partner_id.get_oib_from_vat()  # pravi OIB
        else:
            # TODO: on convert write oib from cert to SPEC field!
            oib = self.fiskal_uredjaj_id.prostor_id.company_id.spec  # OIB IT firme, tj.. oib iz certa!
            if oib.startswith('HR'):
                oib = oib[2:]

        dat_vrijeme = datetime.datetime.strptime(self.vrijeme_izdavanja, '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%YT%H:%M:%S')

        if not dat_vrijeme:
            dat_vrijeme = time_start['datum_vrijeme']
            self.vrijeme_izdavanja = time_start['datum_racun']

        iznos_ukupno = self._fiskal_num2str(self.amount_total)

        # DB: realy? fiscalize foreign currency invoice?
        #     - should not happen , except if customer is pertol station,
        #       or exchange office... only them can accept foreign currency!
        # if 'lcy_amount_total' in self._fields:
        #     iznos_ukupno = fiskal_num2str(self.lcy_amount_total)
        # if 'amount_total_company_signed' in self._fields:  # v10
        #     iznos_ukupno = fiskal_num2str(self.amount_total_company_signed)

        br_rac = self.fiskalni_broj.split(self.company_id.fiskal_separator)
        assert len(br_rac) == 3, "Invoice must be assembled using 3 values!"
        br_rac = fisk.BrRac(data={
            "BrOznRac": br_rac[0],
            "OznPosPr": br_rac[1],
            "OznNapUr": br_rac[2],
            })

        prostor = self.fiskal_uredjaj_id.prostor_id
        u_sustavu_pdv = self.company_id.obracun_poreza != 'none'
        data = {
            "Oib": str(oib),
            "DatVrijeme": dat_vrijeme,
            "OznSlijed": str(self.fiskal_uredjaj_id.prostor_id.sljed_racuna),  # 'P'/'N'
            "USustPdv": u_sustavu_pdv and 'true' or 'false',  # string!
            "NacinPlac": str(self.nacin_placanja),
            "OibOper": str(self.fiskal_user_id.partner_id.get_oib_from_vat()),  # "12345678901"
            "IznosUkupno": iznos_ukupno,
            "BrRac": br_rac,  # get 1. element of tuple
            # ?"SpecNamj": "Tekst specijalne namjene",
            "NakDost": "false",
        }
        if self.paragon_br_rac:
            data['ParagonBrRac'] = str(self.paragon_br_rac)

        if u_sustavu_pdv:
            tax_data = self._prepare_fisk_racun_taxes()
            data.update(tax_data)  # adds tax_data to data dict

        # TODO rutina koja provjerava jel prvi puta ili ponovljeno slanje!
        # Što ako se promijenio zki, a račun je isprintan i predat kupcu?
        if self.zki:
            data['NakDost'] = "true"
        return data

    def fiskaliziraj(self, msg_type='racun'):
        """ Fiskalizira jedan izlazni racun ili point of sale račun
        """
        if self.jir and len(self.jir) > 30:
            return False  # vec je prosao fiskalizaciju

        time_start = self.company_id.get_l10n_hr_time_formatted()
        if not self.fiskal_user_id:
            # MUST USE CURRENT user for fiscalization!
            self.fiskal_user_id = self._uid
        self._fiskal_invoice_valid()

        key, cert, password, production = self.company_id.fiskal_cert_id.get_fiskal_cert_data()
        if not key:
            return False

        fisk.FiskInit.init(key, password, cert, production=production)

        racun_data = self._prepare_fisk_racun(production, time_start)  #
        # pem NOT ENCRYPTED so i send False AS PASSWORD
        racun = fisk.Racun(data=racun_data, key_file=key, key_password=False)
        if not self.zki:
            self.zki = racun.ZastKod              # Zastitni kod is calculated so write it
        racun_zahtjev = fisk.RacunZahtjev(racun)  # create Request
        racun_reply = racun_zahtjev.execute()     # send Request #
        if racun_reply:
            self.jir = racun_reply  # write JIR
        # else:   # DB: no need for this... just leave blank!
        #     cert_type = self.company_id.fina_certifikat_id.cert_type
        #     self.jir = 'PONOVITI SLANJE! ' + cert_type
        time_stop = self.company_id.get_l10n_hr_time_formatted()
        log_vals = self.company_id._get_log_vals(
            msg_type, racun_zahtjev, time_start, time_stop, self.id)
        self.fiskal_log_ids = [0, 0, log_vals]

        # zakucam date iz xml-a! da budemo precizni do kraja!
        self.vrijeme_izdavanja = time_start['odoo_datetime']
        self.vrijeme_xml = racun.DatVrijeme
        fisk.FiskInit.deinit()  # fiskpy deinit - maybe not needed but good for garbage cleaning
        #return True

    def check_fiskalizacija(self):
        pass

class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice", "fiscal.invoice.mixin"]

    # FIELDS
    nacin_placanja = fields.Selection(
        selection_add=[
            ('G', 'GOTOVINA'),
            ('K', 'KARTICE'),
            ('C', 'ČEKOVI'),
            ('O', 'OSTALO')])
    fiskal_log_ids = fields.One2many(
        comodel_name='fiskal.log',
        inverse_name='invoice_id',
        string="Poruke fiskalizacije", copy=False)

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and 'supplier' not in res['name']:
            pass
            if not self.journal_id.fiscal_active:
                res['arch'] = res['arch'].replace(
                    '"Fiskalizacija">',
                    '"Fiskalizacija" invisible="1">')
                #print res['arch']
        return res

    # METHODS
    def get_fiskal_taxes(self, a):
        #res = []
        def get_factory(val):
            fiskal_type = val.get('fiskal_type', False)

            if fiskal_type == 'pdv':
                tns = {'tns': (a.racun.Pdv.Porez, 'tns:Porez'),
                       'fields': ('Stopa', 'Osnovica', 'Iznos')}
            elif fiskal_type == 'pnp':
                tns = {'tns': (a.racun.Pnp.Porez, 'tns:Porez'),
                       'fields': ('Stopa', 'Osnovica', 'Iznos')}
            elif fiskal_type == 'ostali':
                tns = {'tns': (a.racun.OstaliPor.Porez, 'tns:Porez'),
                       'fields': ('Naziv', 'Stopa', 'Osnovica', 'Iznos')}
            elif fiskal_type == 'naknade':
                tns = {'tns': (a.racun.Naknade, 'tns:Naknada'),
                       'fields': ('NazivN', 'IznosN')}
            elif fiskal_type == 'oslobodenje':
                tns = {'tns': (a.racun.IznosOslobPdv),
                       'value': 'Osnovica'}
            elif fiskal_type == 'ne_podlijeze':
                tns = {'tns': (a.racun.IznosNePodlOpor),
                       'value': 'Osnovica'}
            elif fiskal_type == 'marza':
                tns = {'tns': (a.racun.IznosMarza),
                       'value': 'Osnovica'}
            else:
                # raise ?
                return False
            place = tns.get('tns', False)
            if not place:
                # raise?
                return False
            if len(place) > 1:
                porez = a.client2.factory.create(place[1])
                place[0].append(porez)
            else:
                porez = place[0]

            if tns.get('fields', False):
                for field in tns['fields']:
                    porez[field] = val[field]

            if tns.get('value', False):
                tns['tns'][0] = val[field]

            return tns

        for tax in self.tax_line_ids:
            if not tax.tax_id.hr_fiskal_type:
                # MOZDA raise error?
                continue #TODO special cases without tax code, or with base tax code without tax if found
            val = {
                #'tax_code': tax.tax_code_id.id,
                'fiskal_type': tax.tax_id.hr_fiskal_type,
                'Naziv': tax.display_name,
                'Stopa': fiskal_num2str(tax.tax_id.amount),
                'Osnovica': fiskal_num2str(tax.base_amount),
                'Iznos': fiskal_num2str(tax.amount),
                #'NazivN': tax.tax_code_id.name,
                 }
            #res.append(val)
            #TODO group and sum by fiskal_type and Stopa hmmm then send 1 by one into factory...
            get_factory(val)
        # return res

    @api.one
    def button_fiskaliziraj(self):
        if not self.jir:
            self.fiskaliziraj()
        #TODO: nova shema ima metodu provjere da li je racun fiskaliziran!
        elif len(self.jir) == 32:  # BOLE: JIR je 32 znaka !
            self.check_fiskalizacija()
            raise UserError('Nema potrebe ponavljati postupak fiskalizacije!')
