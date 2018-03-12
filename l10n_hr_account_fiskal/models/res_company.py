# -*- encoding: utf-8 -*-

import os
from datetime import datetime
from lxml import etree as et
from .. import fisk
from odoo import api, fields, models, _
from odoo.exceptions import UserError, MissingError, ValidationError



class Company(models.Model):
    _inherit = 'res.company'

    fiskal_cert_id = fields.Many2one('crypto.certificate',
        string="Certifikat za fiskalizaciju",
        domain="[('state', '=', 'confirmed')]")

    # TODO : check for OIB in cert, production must match company vat,
    #        demo should match spec or company vat... no others should be allowed!
    spec = fields.Char(
        string='Specijalno', size=1000,
        help="OIB informatičke tvrtke koja održava software, za demo cert mora odgovarati OIBu sa democertifikata",
        )  # OIB STORM COMPUTERS - za demo cert 20142998436

    @api.onchange('fiskal_cert_id')
    def onchange_fiskal_cert(self):
        """
        Maybe put this in field domain later...
        """
        # DB: maybe also:
        # if 'Fiskal' not in self.fiskal_cert_id.usage:
        # but, strict for now...
        if self.fiskal_cert_id.usage not in [
            'Fiskal_DEMO_V1',
            'Fiskal_PROD_V1',
            'Fiskal_DEMO_V2',
            'Fiskal_PROD_V2'
            ]:
            self.fiskal_cert_id = False  # DB: just empty value, no raise...
            # raise ValidationError(_('Selected certificate is not intended for fiscalization purposes!'))



    def _get_log_vals(self, msg_type, msg, time_start, time_stop, odoo_id):
        '''
        Inherit in other modules with proper super to add values
        '''
        #fiskal_prostor_id = invoice_id = pos_order_id = None
        # if msg_type in ('echo', 'prostor_prijava', 'prostor_odjava', 'PoslovniProstor'):
        #     fiskal_prostor_id = odoo_id
        # elif msg_type in ('racun', 'racun_ponovo', 'Racun'):
        #     invoice_id = odoo_id
        # TODO! :) l10n_hr_pos_fiskal
        # elif msg_type in ('mp_racun', 'mp_racun_ponovo', 'MP Racun'):
        #     pos_order_id = odoo_id
        t_obrada = time_stop['time_stamp'] - time_start['time_stamp']
        time_obr = '%s.%s s' % (t_obrada.seconds, t_obrada.microseconds)
        poruka_zahtjev = et.tostring(msg.get_last_request())
        poruka_odgovor = et.tostring(msg.get_last_response())
        greska = msg.get_last_error()
        id_poruke = msg.get_id_msg()  # idPoruke Echo does not have it
        # message datetime Echo request does not have it
        msg_datetime = msg.get_datetime_msg() or time_stop['time_stamp']
        values = {
            'user_id': self._uid,
            'name': id_poruke,
            'msg_type': msg_type,
            'time_stamp': msg_datetime,
            'time_obr': time_obr,
            'sadrzaj': str(poruka_zahtjev),
            'odgovor': str(poruka_odgovor),
            'greska': str(greska),
            #'fiskal_prostor_id': fiskal_prostor_id,
            #'invoice_id': invoice_id,
            'company_id': self.id
        }
        return values

    def _log_fiskal_comunication(self, msg_type, msg, time_start, time_stop, odoo_id):
        '''
        borrow and SMOP rewrite from decodio
        '''
        #DB: lets stick to ORM... easy inherit for pos!
        self.env['fiskal.log'].create(self._get_log_vals())


class FiskalProstor(models.Model):
    _inherit = 'fiskal.prostor'

    # FIELDS
    datum_primjene = fields.Datetime(
        string='Datum',
        help="Datum od kojeg vrijede navedeni podaci")
    radno_vrijeme = fields.Char(
        string='Radno Vrijeme',
        required="True",
        size=1000, # strictly defined!
        default="8-20 pon-pet, 8-14 sub")
    fiskal_log_ids = fields.One2many(
        comodel_name='fiskal.log',
        inverse_name='fiskal_prostor_id',
        string='Logovi poruka',
        help="Logovi poslanih poruka prema poreznoj upravi")
    ulica = fields.Char(string='Ulica', size=100)
    kbr = fields.Char(string='Kućni broj', size=4)
    kbr_dodatak = fields.Char(string='Dodatak kućnom broju', size=4)
    posta = fields.Char(string='Pošta', size=12)
    naselje = fields.Char(string='Naselje', size=35)
    opcina = fields.Char(string='Naziv općine ili grada', size=35)
    prostor_ostalo = fields.Char(
        string='Ostali tipovi adrese',
        size=100,
        help="Ostali tipovi adresa, npr internet trgovina ili pokretna trgovina")


    def get_fiskal_data(self):
        fina_cert = self.company_id.fiskal_cert_id
        if not fina_cert:
            raise MissingError('Cerificate not found! Check company setup!')

        cert_data = self.cert_data_dict(fina_cert)
        #wsdl_file = 'file://' + os.path.join(self._get_module_dir_path(), 'wsdl', file_name)
        #wsdl_file = 'file://' + os.path.join(self._get_module_dir_path(), 'wsdl', cert_data['wsdl'])
        #TODO: check cert state
        #if not (fina_cert.state=='confirmed' and fina_cert.csr and fina_cert.crt):
        #    return False, False, False

        # OLD VERSION - sprema certifikate na lokaciju config datoteke
        #radi ako je server pokrenut sa -c: path = os.path.join(os.path.dirname(os.path.abspath(config.parser.values.config)),'oe_fiskal')
        #path = os.path.join(os.path.dirname(os.path.abspath(config.rcfile)),'certificates')

        # DB: Stavljam certifikate u l10n_hr_account_fiscal/cert_store
        # TODO: definirati neku bolju lokaciju, ova je dodana u .gitignore!
        path = os.path.join(self._get_module_dir_path(), 'cert_store')
        # if not os.path.exists(path):
        #     os.mkdir(path, 0777)  # TODO 0660 or less

        # user cert data
        key_file = os.path.join(path, "{0}_{1}_{2}_key.pem".format(
            self._cr.dbname, self.company_id.id, fina_cert.id))
        cert_file = os.path.join(path, "{0}_{1}_{2}_crt.pem".format(
            self._cr.dbname, self.company_id.id, fina_cert.id))
        # DB: no need, i do this when validating cert,
        #     if this not exists should i raise error?
        # for file in (key_file, cert_file):
        #     if not os.path.exists(file):
        #         with open(file, mode='w') as f:
        #             content = file.endswith('_key.pem') and fina_cert.csr or fina_cert.crt
        #             f.write(content)
        #             f.flush()
        pass # split two comments for folding
        # fina cert
        # ca_list = []
        # for fcert in cert_data['cert']:
        #     crt_file = fcert[0].split('/')[-1]
        #     crt_path = os.path.join(path, crt_file)
        #     if not os.path.isfile(crt_path):
        #         dc = requests.get(fcert[1])
        #         with open(crt_path, 'wb') as c:
        #             c.write(dc.text)
        #     ca_list.append(crt_path)

        return wsdl_file, key_file, cert_file, ca_list

    @api.one
    def button_test_echo(self):
        echo = fisk.EchoRequest("TEST KOMUNIKACIJE - probna poruka")
        echo_reply = echo.execute()
        if echo_reply != False:
            raise UserError(str(echo_reply))
        else:
            errors = echo.get_last_error()
            raise UserError(str(errors))
        # wsdl, key, cert, ca_list = self.get_fiskal_data()
        # a = Fiskalizacija('echo', wsdl, key, cert, oe_obj=self)
        # odgovor = a.echo()

        # wsdl, key, cert , ca_list = self.get_fiskal_data()
        # echo = fisk.EchoRequest("TEST PORUKA")
        # echo_reply = echo.execute()
        # if(echo_reply != False):
        #     print echo_reply
        # else:
        #     errors = echo.get_last_error()
        #     print "EchoRequest errors:"
        #     for error in errors:
        #         print error
        # return odgovor  #echo_reply

    # DB: moved to l10n_hr_account
    # @api.one
    # def button_prijavi_prostor(self):
    #     self.state = 'active'
    #     return self._log_prijava_odjava('prijava')
    #
    # @api.one
    # def button_odjavi_prostor(self):
    #     self.state = 'closed'
    #     return self._log_prijava_odjava('odjava')

    def _log_prijava_odjava(self, msg_type):
        time = self.company_id.get_l10n_hr_time_formatted()
        log_vals = values = {
            'user_id': self._uid,
            'name': 'manual entry',
            'type': msg_type,
            'time_stamp': time['odoo_datetime'],
            'time_obr': 0,
            'sadrzaj': 'AKTIVACIJA PROSTORA',
            'odgovor': '',
            'greska': '',
            'company_id': self.id
        }
        self.fiskal_log_ids = [(0, 0, log_vals)]


class FiskalLog(models.Model):
    _name = 'fiskal.log'
    _description = 'Fiskal messages log'

    # FIELDS
    name = fields.Char(
        string='Oznaka',
        size=64, readonly=True,
        help="Unique communication mark")
    type = fields.Selection(
        selection=[
            ('prijava', 'Prijava prostora'),
            ('odjava', 'Odjava prostora'),
            ('racun', 'Fiskalizacija racuna'),
            ('rac_pon', 'Ponovljeno slanje racuna'),
            ('rac_prov', 'Provjera fiskalizacije računa'), # NOVO!
            ('echo', 'Test poruka '),
            ('other', 'Other types')],
        string='Message type',
        readonly=True)
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice', readonly=True)
    fiskal_prostor_id = fields.Many2one(
        comodel_name='fiskal.prostor',
        string='Office', readonly=True)
    sadrzaj = fields.Text(string='Sent message', readonly=True)
    odgovor = fields.Text(string='Reply', readonly=True)
    greska = fields.Text(string='Error', readonly=True)
    time_stamp = fields.Datetime(string='Time', readonly=True)
    time_obr = fields.Char(string='Vrijeme obrade', readonly=True)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Person',
        readonly=True,
        on_delete='restrict')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=False)
#
