# -*- coding: utf-8 -*-

import poziv_na_broj as pnbr
from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _get_reference_type(self):
        res = super(AccountInvoice, self)._get_reference_type()
        res.append(('pnbr', 'Poziv na broj'))
        return res

    @api.model
    def _get_default_reference_type(self):
        type_inv = self.env.context.get('type', 'out_invoice')
        #TODO: set countries using this reference model somewhere... (multicompany/multicurrency)
        if type_inv in ('out_invoice',):
            return 'pnbr'
        return 'none'

    def _get_partner_bank_id(self):
        #DB: get and select banks, need it for generating payment reference
        company_id = self.env['res.users']._get_company()
        partner_bank_ids = self.env['res.partner.bank'].search(
                            [('partner_id.ref_company_ids', 'in', [company_id.id])])
        return partner_bank_ids and partner_bank_ids[0] or False

    # FIELDS
    reference_type = fields.Selection(
        selection='_get_reference_type',
        default=_get_default_reference_type)
    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        default=_get_partner_bank_id)

    def pnbr_get(self):

        def getP1_P4data(self, what):
            res = ''
            if what == 'partner_code':
                res = self.partner_id.ref or self.partner_id.id
            elif what == 'partner_id':
                res = str(self.partner_id.id)
            elif what == 'invoice_no':
                res = self.number
            elif what == 'invoice_ym':
                res = self.date_invoice[2:4] + self.date_invoice[5:7]
            elif what == 'delivery_ym':
                res = self.date_delivery[2:4] + self.date_delivery[5:7]
            return pnbr.get_only_numeric_chars(res)

        model = self.journal_id.model_pnbr

        P1 = getP1_P4data(self, self.journal_id.P1_pnbr or '')
        P2 = getP1_P4data(self, self.journal_id.P2_pnbr or '')
        P3 = getP1_P4data(self, self.journal_id.P3_pnbr or '')
        P4 = getP1_P4data(self, self.journal_id.P4_pnbr or '')

        res = pnbr.reference_number_get(model, P1, P2, P3, P4)

        cc = self.journal_id.country_prefix and \
             self.company_id.country_id and \
             self.company_id.country_id.code or ''
        return ' '.join((cc, model, res))

    @api.multi
    def action_move_create(self):
        """
        Before creating moves, check for existance of reference
        if no ref exist on invoice, generate one according to journal setup
        :return:
        """
        res = super(AccountInvoice, self).action_move_create()
        for invoice in self:
            if invoice.reference:
                #TODO: check if ref is valid? in_invoice!
                pass
            else:
                if invoice.journal_id.model_pnbr:
                    ref = self.pnbr_get()
                    self.write({'reference': ref})
        return res