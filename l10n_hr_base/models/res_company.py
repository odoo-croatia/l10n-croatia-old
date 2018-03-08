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
    # Fields, DB: all field names not in english in order to avoid colission with other localisations

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

    # DB: Dopuniti sa ostalim opcijama?
    # pravni_oblik = fields.Selection([
    #     ('obrt', 'Obrt'),
    #     ('jdoo', 'J.D.O.O.'),
    #     ('doo', 'D.O.O.'),
    #     ('dd', 'D.D'),
    #     ('jtd', 'J.T.D'), # Javno trgovačko društvo
    #     ('kd', 'K.D'),    # Komanditno društvo
    #     ('pred', 'Predstavništvo'),
    # ], 'Pravni oblik')
    #     #default='doo', required=True)


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
            'datum_meta': tstamp.strftime('%Y-%m-%dT%H:%M:%S'),     # format za metapodatke xml-a ( JOPPD...)
            'datum_racun': tstamp.strftime('%d.%m.%Y %H:%M:%S'),    # format za ispis na računu
            'time_stamp': tstamp,                                   # timestamp, za zapis i izračun vremena obrade
            'odoo_datetime': time_now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        }
