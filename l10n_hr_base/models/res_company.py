# -*- encoding: utf-8 -*-

import pytz
from tzlocal import get_localzone
from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class Company(models.Model):
    _inherit = "res.company"



    @api.depends('country_id')
    def _check_origin_croatia(self):
        for company in self:
            company.croatia = company.country_id and company.country_id.code == 'HR'

    croatia = fields.Boolean(
        string="Croatia",
        compute="_check_origin_croatia",
        #technical field for show/hide croatia settings, never to be exposed to UI, alwasy invisible!
    )
    # Fields, DB: NAMJERNO SU SVI NAZIVI NA HRVATSKOM!

    nkd = fields.Char(
        string="NKD", size=16,
        help="Šifra glavne djelatnosti prema NKD-2007"
    )
    mirovinsko = fields.Char(
        string='Mirovinsko',
        help='Broj obveznika uplaćivanja mirovinskog osiguranja')
    zdravstveno = fields.Char(
        string='Zdravstveno',
        help='Broj obveze uplaćivanja zdravstvenog osiguranja')
    maticni_broj = fields.Char(string='Matični broj')


    # datum_osnivanja = fields.Date(string='Datum osnivanja')
    # datum_izmjene = fields.Date(
    #     string="Datum zadnje izmjene", readonly=True,
    #     help="Datum zadnje izmjene/dopune pravnih ili poreznih podataka")
    # pravni_oblik = fields.Selection([#TODO: Dopuniti sa ostalim opcijama?
    #     ('obrt', 'Obrt'),
    #     ('jdoo', 'J.D.O.O.'),
    #     ('doo', 'D.O.O.'),
    #     ('dd', 'D.D'),
    #     ('jtd', 'J.T.D'), # Javno trgovačko društvo
    #     ('kd', 'K.D'),    # Komanditno društvo
    #     ('pred', 'Predstavništvo'),
    # ], 'Pravni oblik')
    #     #default='doo', required=True)
    #
    # history_ids = fields.One2many(
    #     comodel_name="res.company.history",
    #     inverse_name="company_id",
    #     string="Legal history",
    #     help="Legal and taxative history data"
    # )
    # #DB: a little extra features, this is used in l10n_hr_account and other modules, for printed reports
    # #    - maybe it could be in some other module, but, for now, let's leave it here
    # address_space_side = fields.Selection(selection=[
    #     ('Left', 'Left'),
    #     ('Right', 'Right')], string='Address space side', help='Side where address will be printed',
    #     default="Left", required=True)
    # DB: mozda ovjde odmah dodati i temeljni kapital, članove uprave i sl... obvezni elementi računa
    # pa kasnije iskoristim za legalno zaglavlje i podnozje računa u l10n_hr_account modulu...

    def get_l10n_hr_time_formatted(self):
        # OLD WAY: tstamp = datetime.now(pytz.timezone('Europe/Zagreb'))
        # DB: Server bi morao biti na UTC time...
        # ali ovo vraća točan local time za any given server timezone setup
        # even if server is on Sidney local time, fiscal time is still in Zagreb :)
        zg = pytz.timezone('Europe/Zagreb')
        server_tz = get_localzone()
        time_now = pytz.utc.localize(datetime.utcnow()).astimezone(server_tz)
        tstamp = zg.normalize(time_now)
        return {
            'datum': tstamp.strftime('%d.%m.%Y'),                   # datum_regular SAD
            'datum_vrijeme': tstamp.strftime('%d.%m.%YT%H:%M:%S'),  # format za zaglavlje FISKAL XML poruke
            'datum_meta': tstamp.strftime('%Y-%m-%dT%H:%M:%S'),    # format za metapodatke xml-a ( JOPPD...)
            'datum_racun': tstamp.strftime('%d.%m.%Y %H:%M:%S'),    # format za ispis na računu
            'time_stamp': tstamp,                                   # timestamp, za zapis i izračun vremena obrade
            'odoo_datetime': time_now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        }
    #
    # def datum_zadnje_izmjene(self):
    #     self.datum_izmjene = fields.date.today()

    # def _get_history_for(self, type, last=False):
    #     """
    #     :param type: type of history data
    #     :return: dict with (list of all) history data for type
    #     """
    #     res = [{'id': x.id,
    #             'type': type,
    #              'old_value': x.old_value,
    #              'old_string': x.old_string,
    #              'new_value': x.new_value,
    #              'new_string': x.new_string,
    #              'date_start': x.date_start,
    #              'date_end': x.date_end} for x in self.history_ids
    #             if x.type == type and last and not x.date_end]
    #     return last and res and res[0] or res
    #
    # def _get_write_value(self, get_field, value):
    #     field = self._fields[get_field]
    #     field_selection = False
    #     try:
    #         field_selection = field.selection
    #     except:
    #         pass
    #
    #     if field_selection:
    #         for sel in field_selection:
    #             if value == sel[0]:
    #                 return sel
    #     else:  # m2o: porezna
    #         name = '(), ""'
    #         if type(value) == int:
    #             name = self.env.get(field.comodel_name).browse(value).name_get()[0]
    #         else:  # dosao browse record
    #             name = value.name_get()[0]
    #         return name
    #
    # def _get_fields_to_check(self):
    #     """
    #     inherit in other modules to check more fields
    #     """
    #     res = {
    #         # 'porezna_id': {},
    #         'pravni_oblik': {},
    #         # 'obracun_period': {}, -> l10n_hr_vat
    #         'obracun_poreza': {}
    #     }
    #     return res
    #
    #
    # def write(self, vals):
    #     #TODO: check if this we need!
    #     # check_values = self._get_fields_to_check()
    #     # history_ids = []
    #     # for check in check_values:
    #     #     if check in vals and vals[check]:
    #     #         old_value = eval('self.' + check)
    #     #         if old_value:
    #     #             old = self._get_write_value(check, old_value)
    #     #         else:
    #     #             old = (False, False)
    #     #         new = self._get_write_value(check, vals[check])
    #     #         history = self._get_history_for(check, last=True)
    #     #         date_start = fields.Date.today()
    #     #         if history:
    #     #             history.update({'date_end': date_start})
    #     #             history_ids.append((0, history['id'], history))
    #     #         else:
    #     #             date_start = self.datum_osnivanja and self.datum_osnivanja or date_start
    #     #         history_ids.append((0, 0, {'type': check,
    #     #                                    'old_value': old[0],
    #     #                                    'old_string': old[1],
    #     #                                    'new_value': new[0],
    #     #                                    'new_string': new[1],
    #     #                                    'date_start': date_start,
    #     #                                    'date_end': False}))
    #     # if history_ids:
    #     #     vals.update({'history_ids': history_ids})
    #     return super(Company, self).write(vals)
    #
    # @api.onchange('datum_osnivanja')
    # def _onchange_datum_osnivanja(self):
    #     if self.history_ids and self.datum_osnivanja:
    #         new_history = [(1, x['id'], {'date_start': self.datum_osnivanja})
    #                        for x in self.history_ids if not x.date_start]
    #         # DB: jednostavno update samo ako nema date start...
    #         if new_history:
    #             self.history_ids = new_history
    #             self.datum_zadnje_izmjene()
    #



# class CompanyHistory(models.Model):
#     _name = 'res.company.history'
#     _description = 'Company legal/taxative history'
#     _order = "type, date_start"
#
#     company_id = fields.Many2one(
#         comodel_name='res.company',
#         string='Company', required=True
#     )
#     type = fields.Selection(
#         selection=[
#             ('porezna_id', 'Porezna uprava'),     # preselio sjediste, moguć slučaj, datum primjene: 1. u sljedecm periodu
#             ('pravni_oblik', 'Pravni oblik'),     # j.d.o.o. -> d.o.o malo vjerojatnan slucaj, mozda jos neki?
#             ('obracun_poreza', 'Obračun poreza'), # R1 -> R2 , samo početak godine
#             ('obracun_period', 'Period poreza')],  # kvartalni u mjesecni -> ulaskom u VIES, kraj trenutnog perioda! ili pocetak godine
#         string="Type", required=True
#     )
#     old_value = fields.Char(string='Old value')
#     old_string = fields.Char(string='Old string')
#     new_value = fields.Char(string='New value')
#     new_string = fields.Char(string='New string')
#     date_start = fields.Date(string='Date start')
#     date_end = fields.Date(string='Date end')
#
#     #TODO : kontrole preklapanja perioda , sljedeći datum isl...
