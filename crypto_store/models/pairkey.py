# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import os
from M2Crypto import BIO, Rand, SMIME, EVP, RSA, X509
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CryptoPairkey(models.Model):
    _name = "crypto.pairkey"
    _description = 'Crypto keypair store'


    ## Fields
    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', 'Owner',
                              help='Owner of the key. The only who can view, import and export the key.')
    group_id = fields.Many2one('res.groups', 'User group',
                              help='Users who can use the pairkey.')
    pub = fields.Text('Public key',
                      readonly=True, states={'draft': [('readonly', False)]},
                      help='Public key in PEM format.')
    key = fields.Text('Private key',
                      readonly=True, states={'draft': [('readonly', False)]},
                      help='Private key in PEM format.')
    state = fields.Selection([
                ('draft', 'Draft'),
                ('confirmed', 'Confirmed'),
                ('cancel', 'Cancelled'),
            ], 'State', readonly=True, default='draft',
            help='* The \'Draft\' state is used when a user is creating a new pair key. Warning: everybody can see the key.\
            \n* The \'Confirmed\' state is used when the key is completed with public or private key.\
            \n* The \'Canceled\' state is used when the key is not more used. You cant use this key again.')


    #METHODS
    @api.multi
    def action_validate(self):
        for pk in self:
            # Check public key
            try:
                PUB = BIO.MemoryBuffer(self.pub.encode('ascii'))
                RSA.load_pub_key_bio(PUB)
                pub = True
            except:
                pub = False
            # Check private key
            try:
                RSA.load_key_string(self.key.encode('ascii'))
                key = True
            except:
                key = False
            if key or pub:
                self.state = 'confirmed'
            else:
                raise UserError(_('Cannot confirm invalid pairkeys. You need provide private and public keys in PEM format.'))

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    def action_generate(self):
        self.generate_keys()
        return self.action_validate(cr, uid, ids, context=context)

    @api.one
    def as_pem(self):
        """
        Return pairkey in pem format.
        """
        private = self.key and self.key.encode('ascii') or ''
        public = self.pub and self.pub.encode('ascii') or ''
        return '\n'.join((private, public))

    @api.one
    def as_rsa(self):
        """
        Return RSA object.
        """
        return RSA.load_key_string(self.as_pem()[0])

    @api.one
    def as_pkey(self):
        """
        Return PKey object.
        """
        # def set_key(rsa):
        #     pk = EVP.PKey()
        #     pk.assign_rsa(rsa)
        #     return pk
        # return dict((k, set_key(v)) for k, v in self.as_rsa().items())
        pk = EVP.PKey()
        pk.assign_rsa(self.as_rsa()[0])
        return pk


    @api.one
    def generate_keys(self, key_length=2048, key_gen_number=0x10001):
        """
        Generate key pairs: private and public.
        """
        # Random seed
        Rand.rand_seed (os.urandom(key_length))
        # Generate key pair
        key = RSA.gen_key (key_length, key_gen_number, lambda *x: None)
        # Create memory buffers
        pri_mem = BIO.MemoryBuffer()
        pub_mem = BIO.MemoryBuffer()
        # Save keys to buffers
        key.save_key_bio(pri_mem, None)
        key.save_pub_key_bio(pub_mem)

        self.key = pri_mem.getvalue()
        self.pub = pub_mem.getvalue()
        pass

    @api.one
    def generate_certificate_request(self, x509_name, cert_id=False):
        """
        Generate new certificate request for pairkey.
        """
        # Create certificate structure
        pk = EVP.PKey()
        req = X509.Request()
        if not self.key or not self.pub:
            raise UserError(_('Missing keys for request generation!'))
        pem_string = self.key.encode('ascii') + '\n' + self.pub.encode('ascii')
        rsa = RSA.load_key_string(pem_string)
        pk.assign_rsa(rsa)
        req.set_pubkey(pk)
        req.set_subject(x509_name)

        # Crete certificate object
        cert_obj = self.env['crypto.certificate']
        if cert_id:
            co = cert_obj.browse(cert_id)
            co.write({'csr': req.as_pem()})
        else:
            cert_obj.create({
                'name': x509_name.as_text(),
                'csr': req.as_pem(),
                'pairkey_id': self.id,
            })

