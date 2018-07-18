# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class AccountTax(models.Model):
    _inherit = 'account.tax'

    #DB: netrebam fiskal_percent...
    hr_fiskal_type = fields.Selection(
        selection=[
            ('pdv', 'PDV'),
            ('pnp', 'Porez na potrosnju'),
            ('ostali', 'Ostali porezi'),
            ('oslobodenje', 'Oslobodjenje'),
            ('marza', 'Oporezivanje marze'),
            ('ne_podlijeze', 'Ne podlijeze oporezivanju'),
            ('naknade', 'Naknade (npr. ambalaza)')],
        string="Fiskalni tip poreza",
        domain="[('type_tax_use', '!=', 'purchase')]")
