# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        res = super(AccountMove, self).post()
        invoice = self.env.context.get('invoice', False)
        if invoice and \
            invoice.type in ('out_invoice', 'out_refund') and \
            invoice.company_id.croatia:
            if invoice.journal_id.fiscal_active:
                invoice.fiskaliziraj()
            else:
                if invoice.nacin_placanja != 'T':
                    raise ValidationError("Odabrani način plaćanja nije dozvoljen "\
                                          "jer fiskalizacija nije aktivna za dnevnik '%s'" % \
                                          invoice.journal_id.name)
        return res
