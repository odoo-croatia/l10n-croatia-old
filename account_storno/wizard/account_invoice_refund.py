# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
#from odoo.tools.safe_eval import safe_eval as eval
#from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    @api.model
    def _get_reason(self):
        res = super(AccountInvoiceRefund, self)._get_reason()
        context = dict(self.env.context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
            if inv.journal_id.posting_policy =='storno':
                res = _('Storno ') + inv.number
            else:
                res = _('Refund ') + inv.number
        return res

    description = fields.Char(default=_get_reason) # need to trigger override method!

    @api.multi
    def compute_refund(self, mode='refund'):
        ctx = dict(self.env.context, refund_mode=mode)
        return super(AccountInvoiceRefund, self.with_context(ctx)).compute_refund(mode)

