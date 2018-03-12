# -*- coding: utf-8 -*-
{
    "name": "Croatia COA - RRIF 2015",
    "summary": "Croatia COA template - RRIF2015",
    "category": "Localization",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "Odoo Hrvatska",
    "support": "support@odoo-hrvatska.org",
    "website": "http://odoo-hrvatska.org",
    "licence": "LGPL-3",
    "depends": [
        "account",
        "base_vat",
        "base_iban",
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "data": [
        "data/l10n_hr_account_chart_data.xml", #DB: template id = l10n_hr_coa_rrif_2015_template
        "data/account.account.type.csv",
        "data/account.tax.group.csv", # 9.11.2017 dodan na template field tax_group_id!
        "data/account.account.tag.csv",
        "data/account.account.template.csv",
        "data/company_croatia.xml",
        "data/account.tax.template.csv",
        "data/account.fiscal.position.template.csv",
        "data/account.fiscal.position.tax.template.csv",
        "data/account.fiscal.position.account.template.csv",
        "data/account_tax_group_data.xml",
        "data/account_chart_template_apply.yml",
    ],
    "qweb": [],
    "demo": [],

    "auto_install": False,
    "installable": True,
    "post_init_hook": '_install_l10n_hr_modules',
}


