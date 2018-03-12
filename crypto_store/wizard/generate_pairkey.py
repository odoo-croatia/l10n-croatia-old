# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

class CryptoGeneratePairkey(models.TransientModel):
    _name = 'crypto.generate.pairkey'


    name = fields.Char('Pair key name')
    key_length = fields.Integer('Key lenght', default=2048)
    update = fields.Boolean('Update key')

    @api.one
    def on_generate(self):
        active_ids = self._context['active_id']
        pairkey_obj = self.env['crypto.pairkey'].browse(active_ids)

        pairkey_obj.generate_keys(key_length=self.key_length)
        pairkey_obj.action_validate()
        return {'type': 'ir.actions.act_window_close'}


    def on_cancel(self):
        return {}

