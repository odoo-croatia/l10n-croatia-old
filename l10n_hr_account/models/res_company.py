# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Company(models.Model):
    _inherit = 'res.company'

    # Fields

    fiskal_prostor_ids = fields.One2many(
        comodel_name='fiskal.prostor',
        inverse_name='company_id',
        string='Business premises')
    fiskal_separator = fields.Selection(
        selection=[
            ('/', '/'),
            ('-', '-')],
        string="Invoice number separator",
        default='/', # required=True,    -> multicompany, moved required to view
        help="Only '/' or '-' are legaly defined as allowed"
    )
    obracun_poreza = fields.Selection(
        selection=[
            ('none', 'Nije u sustavu PDV'),
            ('r2', 'Po naplaćenom računu (R2)'),
            ('r1', 'Po izdanom računu (R1)')],
        string='Obračun poreza',
        help="Odabir utiče na izgled i sadržaj ispisanog računa") #, required=True) -> moved to view



class FiskalProstor(models.Model):
    _name = 'fiskal.prostor'
    _description = 'Poslovni prostori - fiskalizacija'

    #Fields
    lock = fields.Boolean(
        string="Lock",
        help="Jednom kad se napravi prvi račun oznaka prostora i sljed računa se više nesmiju mijenjati"
    )
    name = fields.Char(
        string='Name', size=128)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required="True",
        default=lambda self: self.env['res.company']._company_default_get('fiskal.prostor'))
    user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='fiskal_prostor_res_users_rel',
        column1='prostor_id', column2='user_id',
        string='Allowed users')

    oznaka_prostor = fields.Char(
        string='Code',
        required="True", size=20)
    sljed_racuna = fields.Selection(
        selection=[
            ('N', 'Na nivou naplatnog uredjaja'),
            ('P', 'Na nivou poslovnog prostora')],
        string='Sequence by',
        required="True",
        default='P')
    mjesto_izdavanja = fields.Char(
        string="Mjesto izdavanja računa", required="True",
        help="Mjesto izdavanja računa, ispisati na računu kao obavezan podatak"
    )
    uredjaj_ids = fields.One2many(
        comodel_name='fiskal.uredjaj',
        inverse_name='prostor_id',
        string='Uredjaji')
    state = fields.Selection(
        selection=[
            ('draft', 'Nacrt'),
            ('active', 'Aktivan'),
            ('closed', 'Zatvoren')],
        string='State',
        default='draft')
    journal_ids = fields.One2many(
        comodel_name='account.journal',
        inverse_name='prostor_id',
        string="Journals",
        help="Sale journals for this business premisse")

    _sql_constraints = [
            ('fiskal_prostor_uniq',
             'unique (oznaka_prostor,company_id)',
             'The code of the business premise must be unique per company !')
        ]

    @api.one
    def button_prijavi_prostor(self):
        self.state = 'active'
        if self.env.get('l10n_hr_account_fiskal'):
            return self._log_prijava_odjava('prijava')

    @api.one
    def button_odjavi_prostor(self):
        self.state = 'closed'
        if self.env.get('l10n_hr_account_fiskal'):
            return self._log_prijava_odjava('odjava')

    @api.model
    def unlink(self):
        for ured in self:
            if ured.lock:
                raise ValidationError('Nije moguće brisati uređaj na kojem je izdan račun!')
        return super(FiskalProstor, self).unlink()




class FiskalUredjaj(models.Model):
    _name = 'fiskal.uredjaj'
    _description = 'Podaci o naplatnim uredjajima'


    lock = fields.Boolean(
        string="Lock", default=False,
        help="Jednom kad se napravi prvi račun oznaka uređaja se više nesmije mijenjati"
    )
    name = fields.Char(
        string='Naziv naplatnog uredjaja')
    prostor_id = fields.Many2one(
        comodel_name='fiskal.prostor',
        string='Prostor',
        help='Prostor naplatnog uredjaja',
        ondelete="restrict")
    oznaka_uredjaj = fields.Integer(
        string='Oznaka naplatnog uredjaja',
        required="True")
    user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='fiskal_uredjaj_res_users_rel',
        column1='uredjaj_id', column2='user_id',
        string='Korisnici s pravom knjiženja')
    journal_ids = fields.Many2many(
        comodel_name='account.journal',
        relation='fiskal_uredjaj_account_journal_rel',
        column1='uredjaj_id', column2='journal_id',
        string='Dnevnici',
        domain="[('type', 'in', ['sale','sale_refund'])]")
    aktivan = fields.Boolean(
        string='Aktivan',
        default=True)

    _sql_constraints = [
        ('fiskal_uredjaj_uniq',
         'unique (oznaka_uredjaj,prostor_id)',
         'The code of the payment register must be unique per business premise !')
    ]

    # Methods
    @api.multi
    def name_get(self):
        res = []
        for ured in self:
            res.append((ured.id, "%s-%s" % (ured.prostor_id.name, ured.name)))
        return res

    @api.model
    def unlink(self):
        for ured in self:
            if ured.lock:
                raise ValidationError('Nije moguće brisati uređaj na kojem je izdan račun!')
        return super(FiskalUredjaj, self).unlink()
