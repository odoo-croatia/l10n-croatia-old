# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('property_account_position_id')
    def _onchange_fiscal_position_id(self):
        '''
        let's just map account on partner when fiskal position is selected
        :return: new accounts mapped according to fis_pos
        '''
        if self.property_account_position_id:
            acc_fis_pos = self.env['account.fiscal.position'].browse(
                self.property_account_position_id.id)
            self.property_account_payable_id = acc_fis_pos.map_account(
                self.property_account_payable_id)
            self.property_account_receivable_id = acc_fis_pos.map_account(
                self.property_account_receivable_id)

    def get_oib_from_vat(self):
        oib = self.vat
        if oib.startswith('HR') and self.company_id.croatia:
            oib = oib[2:]
        else:
            oib = False
        return oib

    # @api.multi
    # def get_history_data(self):
    #     res = {}
    #     for partner in self:
    #         res.update({partner.id: {
    #                 'vat': partner.vat and partner.vat or _('NO VAT No. entry'),
    #                 'name': partner.name,
    #                 'street': partner.street and partner.street or _('NO Street entry'),
    #                 'city': partner.city and partner.city or _('NO City entry'),
    #                 'zip': partner.zip and partner.zip or _('NO Zip entry')
    #                 }})
    #     return res