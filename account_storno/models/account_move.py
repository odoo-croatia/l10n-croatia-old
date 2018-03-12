# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _auto_init(self):
        result = super(AccountMoveLine, self)._auto_init()
        # Remove constrains for credit_debit1unt_move_line_credit_debit2", credit_debit2
        # DB: need to find a way to run this... still not working!
        self._cr.execute("""
            ALTER TABLE account_move_line
            DROP CONSTRAINT IF EXISTS account_move_line_credit_debit2;
        """)
        return result

    # _sql_constraints = [
    #     ('credit_debit4',
    #      'CHECK (abs(credit+debit)>=0)',
    #      'Wrong credit or debit value in accounting entry !'),
    # ]

    @api.multi
    def _check_contra_minus(self):
        """
        This is to restore credit_debit2 check functionality, for contra journals
        """
        for l in self:
            if l.journal_id.posting_policy == 'contra':
                if l.debit + l.credit < 0.0:
                    return False
        return True

    @api.multi
    def _check_side(self):
        """
        For Storno accounting some account are using only one side during FY
        """
        for l in self:
            check_side = l.account_id.check_side
            if (check_side and (
                    check_side == 'debit' and abs(l.credit) > 0.0 or
                    check_side == 'credit' and abs(l.debit) > 0.0)):
                return False
        return True

    _constraints = [
            (_check_contra_minus, _(
                'Negative credit or debit amount is not allowed for "contra" journal policy.'), ['journal_id']),
        ]

