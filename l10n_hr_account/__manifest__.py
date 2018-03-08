# -*- coding: utf-8 -*-
{
    "name": "Croatia - Accounting base",
    "summary": "Croatia accounting localisation",
    "category": "Localisation / Croatia",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "Odoo hrvatska"
              "Storm Computers" 
              "DAJ MI 5!",
    "support": "support@odoo-hrvatska.org",
    "website": "http://odoo-hrvatska.org",
    "licence": "LGPL-3",
    "depends": [
        "account_accountant",
        "account_storno",
        "base_vat",
        "l10n_hr_base",
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "data": [
        "views/res_config_view.xml",
        "views/res_company_view.xml",
        "views/res_users_view.xml",
        "views/account_invoice_view.xml",
        "views/account_journal_view.xml",
        #"views/report_invoice.xml",
        "views/reports_menu.xml",
        "security/ir.model.access.csv",
    ],
    "qweb": [],
    "demo": [],

    "auto_install": False,
    "installable": True,
}


