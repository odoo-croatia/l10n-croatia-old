# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    croatia = fields.Boolean(related="company_id.croatia")

    module_l10n_hr_account_fiskal = fields.Boolean(
        string="Koristi fiskalizaciju računa",
        help="Ova opcija instalira modul l10n_hr_fiskal")

    module_account_reference = fields.Boolean(
        string="Koristi poziv na broj u izlaznim računima",
        help="Ova opcija instalira modul account_reference")

    # TODO:
    # module_l10n_hr_vat = fields.Boolean(
    #     string="Hrvatski porezni izvještaji",
    #     help="Ova opcija instalira modul l10n_hr_vat")

    # module_l10n_hr_joppd = fields.Boolean(
    #     string="JOPPD obrazac",
    #     help="Ova opcija instalira modul l10n_hr_joppd")
