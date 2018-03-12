# -*- coding: utf-8 -*-
{
    "name": "Croatia COA - RRIF 2015 - tax cash basis",
    "summary": "Croatia COA template - RRIF2015 - tax cash basis setup",
    "category": "Localization",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "Odoo Hrvatska"
              "DAJ MI 5!",
    "support": "support@odoo-hrvatska.org",
    "website": "http://odoo-hrvatska.org",
    "licence": "LGPL-3",
    # "price" : 20.00,   #-> only if module if sold!
    # "currency": "EUR",

    "depends": [
        "l10n_hr_coa_rrif_2015",
        "account_tax_cash_basis",
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "data": [
        "data/correct_taxes.yml",
        "data/account_tax_group_data.xml",
        "data/account_tax_data.xml",
        "data/account_fiscal_position_data.xml",
        "data/account_journal.xml",
        "data/setup_journal.yml",
    ],
    "qweb": [],
    "demo": [],

    "auto_install": True,
    "installable": True,
    "post_init_hook": '',
}


