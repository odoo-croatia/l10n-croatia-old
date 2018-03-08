# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Bank(models.Model):
    _inherit = 'res.bank'

    # Fields
    vbb_code = fields.Char(
        string='VBB',
        help="Vodeći broj banke")
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        help="Partner representing this bank")


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"


    def _bank_from_vbb_code(self, bank_acc):
        if not bank_acc:
            return False
        vbb = bank_acc.replace(' ', '')[4:11]
        bank = self.env['res.bank'].search([('vbb_code', '=', vbb)])
        return bank and bank[0].id or False

    @api.model
    def create(self, vals):
        if 'bank_id' not in vals or not vals['bank_id']:
            vals['bank_id'] = self._bank_from_vbb_code(vals['acc_number'])
        return super(ResPartnerBank, self).create(vals)
