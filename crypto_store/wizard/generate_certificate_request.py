# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from M2Crypto import X509
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CryptoGenerateCertificateRequest(models.TransientModel):
    _name = 'crypto.generate.certificate.request'

    #Fields
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'crypto.generate.certificate.request'))
    name_c = fields.Char('Country (C)', size=2)
    name_sp = fields.Char('State or Province Name (ST/SP)', size=64)
    name_l = fields.Char('Locality Name (L)', size=64)
    name_o = fields.Char('Organization Name (O)', size=64)
    name_ou = fields.Char('Organization Unit Name (OU)', size=64)
    name_cn = fields.Char('Common name (CN)', size=64)
    name_gn = fields.Char('Given Name (GN)', size=64)
    name_sn = fields.Char('Surname (SN)', size=64)
    name_email = fields.Char('E-mail Addres (EMail)', size=64)
    name_serialnumber = fields.Char('Serial Number (serialNumber)', size=64)

    @api.onchange('company_id')
    def onchange_company_id(self):
        company_addr = self.company_id.partner_id
        try:
            self.name_c = company_addr.country_id.code
            self.name_sp = company_addr.state_id.name
            self.name_l = company_addr.city
            self.name_o = company_addr.name
            self.name_cn = company_addr.name
            self.name_email = company_addr.email
        except:
            pass

    @api.one
    def on_generate(self):
        active_model = self._context['active_model']
        active_obj = self.env[active_model].browse(self._context['active_id'])
        cert_id = False
        if active_model == 'crypto.certificate':
            if not active_obj.pairkey_id:
                raise UserError('Key pairs missing!')
            cert_id = active_obj.id
            pairkey_obj = active_obj.pairkey_id
        elif active_model == 'crypto.pairkey':
            c_id = self.env['crypto.certificate'].search([('pairkey_id', '=', active_obj.id)])
            if c_id and len(c_id) == 1:
                cert_id = c_id[0]
            elif c_id and len(c_id) > 1:
                #DB: mozda provjeriti koji da uzme??
                cert_id = c_id[0]
            pairkey_obj = active_obj

        name = X509.X509_Name()
        if self.name_c:  name.C  = self.name_c
        if self.name_sp: name.SP = self.name_sp
        if self.name_l:  name.L  = self.name_l
        if self.name_o:  name.O  = self.name_o
        if self.name_ou: name.OU = self.name_ou
        if self.name_cn: name.CN = self.name_cn
        if self.name_gn: name.GN = self.name_gn
        if self.name_sn: name.SN = self.name_sn
        if self.name_email: name.EMail = self.name_email
        if self.name_serialnumber: name.serialNumber = self.name_serialnumber
        pairkey_obj.generate_certificate_request(name, cert_id=cert_id)
        return {'type': 'ir.actions.act_window_close'}


    def on_cancel(self, cr, uid, ids, context):
        return {}

