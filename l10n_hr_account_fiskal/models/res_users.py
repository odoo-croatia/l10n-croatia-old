# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, MissingError


class Users(models.Model):
    _inherit = 'res.users'

    vat = fields.Char(
        related='partner_id.name',
        inherited=True,
        help="Mandatory only for users that needs to validate invoices")
