# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    # FIELDS
    fiscal_active = fields.Boolean(
        string="Fiskaliziranje računa",
        help="Fiskalizacija aktivna za ovaj dnevnik")
    default_nacin_placanja = fields.Selection(
        selection_add=[
            ('G', 'GOTOVINA'),
            ('K', 'KARTICE'),
            ('C', 'CEKOVI'),
            ('O', 'OSTALO')
        ])