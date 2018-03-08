# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import except_orm
#from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line=line, part=part)
        if self.journal_id.posting_policy == 'storno':
            debit = res.get('debit', False)
            credit = res.get('credit', False)

            # Correct debit and credit
            if line['type'] and (
                (line['type'] in ('src', 'tax') and self.type in ('out_invoice', 'out_refund') and debit) or
                (line['type'] == 'dest' and self.type in ('out_invoice', 'out_refund') and credit) or
                (line['type'] in ('src', 'tax') and self.type in ('in_invoice', 'in_refund') and credit) or
                (line['type'] == 'dest' and self.type in ('in_invoice', 'in_refund') and debit)
            ):
                res.update({
                    'debit': credit and credit * -1.0,
                    'credit': debit and debit * -1.0,
                })


        return res

    @api.model
    def _refund_cleanup_lines(self, lines):
        """ Add analytic_tag_ids """
        result = super(AccountInvoice, self)._refund_cleanup_lines(lines)
        for i in xrange(0, len(lines)):
            for name, field in lines[i]._fields.iteritems():
                if name == 'analytic_tag_ids':
                    result[i][2][name] = [(6, 0, lines[i][name].ids)]
        return result

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        if invoice.type in ('in_refund', 'out_refund'):
            raise except_orm(_('Error!'), _('You cannot refund a Refund.'))
        values = super(AccountInvoice, self)._prepare_refund(
            invoice=invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        if invoice.journal_id.posting_policy == 'storno':
            if self.env.context.get('refund_mode', 'refund') != 'refund':
                values['type'] = invoice.type
                for invoice_line in values['invoice_line_ids']:
                    invoice_line[2]['quantity'] = invoice_line[2].get('quantity', 0.0) * -1.0
                    invoice_line[2]['price_subtotal'] = invoice_line[2].get('price_subtotal', 0.0) * -1.0
                    invoice_line[2]['price_subtotal_signed'] = invoice_line[2].get('price_subtotal_signed', 0.0) * -1.0
                for tax_line in values['tax_line_ids']:
                    tax_line[2]['base'] = tax_line[2].get('base', 0.0) * -1.0
                    tax_line[2]['amount'] = tax_line[2].get('amount', 0.0) * -1.0

        return values

