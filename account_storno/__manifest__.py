# -*- coding: utf-8 -*-
{
    "name": """account_storno""",
    "summary": """'RED' storno full implementation""",
    "category": "Accounting",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "Odoo Hrvatska",
    "support": "support@odoo-hrvatska.org",
    "website": "http://odoo-hrvatska.org",
    "licence": "LGPL-3",
    #"price" : 20.00,   #-> only if module if sold!
    #"currency": "EUR",

    "depends": [
        "account",
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "data": [
        "views/account_journal_view.xml",
    ],
    "qweb": [],
    "demo": [],

    "auto_install": False,
    "installable": True,
}

