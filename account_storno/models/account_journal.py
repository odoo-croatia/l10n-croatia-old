# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    posting_policy = fields.Selection([
        ('contra', 'Contra (debit<->credit)'),
        ('storno', 'Storno (-)')], 'Storno or Contra', required=True, default='storno',
         help="Storno allows minus postings, Refunds are posted on the same journal/account * (-1)."
              "Contra doesn't allow negative posting. Refunds are posted by swapping credit and debit side.")
