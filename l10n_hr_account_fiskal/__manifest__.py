# -*- coding: utf-8 -*-
{
    "name": "Fiskalizacija računa",
    "summary": """Croatia fiscalization module""",
    "category": "Localisation / Croatia",
    "images": [],
    "version": "1.1.0",
    "application": False,

    "author": "Odoo Hrvatska"
              "Slobodni programi"
              "DAJ MI 5!"
              "Storm Computers",
    "support": "support@odoo-hrvatska.org",
    "website": "http://odoo-hrvatska.org",
    "licence": "LGPL-3",
    #"price" : 20.00,   #-> only if module if sold!
    #"currency": "EUR",

    "depends": [
        "l10n_hr_account",
        "crypto_store",
    ],
    "external_dependencies": {
        "python": [
            # 'M2Crypto',
            # 'pyOpenSSL',
        ],
        "bin": [
            'openssl',
            #'python-m2crypto'
        ]
    },
    "data": [
        "views/account_invoice_view.xml",
        "views/account_journal_view.xml",
        "views/account_tax_view.xml",
        "views/res_company_view.xml",
        "views/res_users_view.xml",
        "views/report_invoice.xml",
        "security/ir.model.access.csv",
        # try to update existing known taxes
        #"data/update_taxes.yml" moved to comapny module! not for public... and,
        # also, at install time company data may not be fille dyet
    ],
    "qweb": [],
    "demo": [],

    "auto_install": False,
    "installable": True,
}
