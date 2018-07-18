# -*- encoding: utf-8 -*-


import os
import OpenSSL
from odoo import api, fields, models, _, tools
from odoo.tools import config as odoo_config


class CryptoCertificate(models.Model):
    _inherit = "crypto.certificate"


    @api.one
    @api.depends('csr', 'crt', 'type')
    def _get_usage(self):
        super(CryptoCertificate, self)._get_usage()
        for crt in self:
            if crt.type != 'server_rec':
                continue
            if not crt.csr:
                continue
            try:
                pp = OpenSSL.crypto.load_certificate(1, crt.crt)
            except:
                continue
            c_issuer = pp.get_issuer().get_components()
            cert_issuer_ou, cert_issuer_cn = None, None
            for c in c_issuer:
                if c[0] == 'O':
                    cert_issuer_name = c[1]
                elif c[0] == 'CN':
                    cert_issuer_cn = c[1]
                elif c[0] == 'OU':
                    cert_issuer_ou = c[1]

            c_subject = pp.get_subject().get_components()
            usage = False
            if cert_issuer_ou is not None:  # OLD cert, new cert this is None!
                if cert_issuer_ou == 'DEMO':
                    usage = 'Fiskal_DEMO_V1'
                else:
                    usage = 'Fiskal_PROD_V1'
            else:
                if cert_issuer_cn == 'Fina Demo CA 2014':
                    usage = 'Fiskal_DEMO_V2'
                else:
                    usage = 'Fiskal_PROD_V2'
            crt.usage = usage

    def _get_datastore_path(self):
        return odoo_config.filestore(self._cr.dbname)

    def _get_fiskal_cert_path(self):
        fisk_cert_path = os.path.join(
            self._get_datastore_path(), 'fiskal_cert')
        if not os.path.exists(fisk_cert_path):
            os.mkdir(fisk_cert_path, 4600)  # setuid,rw, minimal rights applied
        return fisk_cert_path

    def _get_key_cert_file_name(self):
        key = "{0}-{1}-{2}_key.pem".format(
            self.usage, self.id, self._cr.dbname)
        crt = "{0}-{1}-{2}_crt.pem".format(
            self.usage, self.id, self._cr.dbname)
        return key, crt

    def _disk_check_exist(self, file):
        return os.path.exists(file)

    def _disk_same_content(self, file, content):
        try:
            with open(file, mode="r") as f:
                on_disk = f.read()
                f.close
        except:
            return True
        return not(on_disk == content)

    def _disk_write_content(self, file, content):
        with open(file, mode="w") as f:
            f.write(content)
            f.flush()

    def get_fiskal_cert_data(self):
        production = 'PROD' in self.usage
        password = self.cert_password
        f_path = self._get_fiskal_cert_path()
        key, cert = self._get_key_cert_file_name()
        for pem in (key, cert):
            file = os.path.join(f_path, pem)
            if pem.endswith('_key.pem'):
                content = self.csr
                key = file
            else:
                content = self.crt
                cert = file

            if self._disk_check_exist(file) or \
                    self._disk_same_content(file, content):
                self._disk_write_content(file, content)

        return key, cert, password, production

    def _check_valid(self):
        res = super(CryptoCertificate, self)._check_valid()
        if self.state == 'draft' and \
           self.status == 'certificate_converted':
            res['state'] = 'confirmed'
            res['msg'] = False
            # e sad kad ga potvrdjujem cu ga i spustiti na disk...
            # f_path = self._get_fiskal_cert_path()
            # for pem in self._get_key_cert_file_name():
            #     with open(os.path.join(f_path, pem), mode="w") as f:
            #         content = pem.endswith('_key.pem') and self.csr or self.crt
            #         f.write(content)
            #         f.flush()
            # self._save_to_disk(f_path)
        return res



    usage = fields.Char(compute="_get_usage", store=True)  # only to trigger _get_usage call here

    @api.one
    def action_cancel(self):
        if 'Fiskalizacija' in self.usage:
            #DB: sad bi ga mogao i obrisati sa diska...Justin Case
            pass




