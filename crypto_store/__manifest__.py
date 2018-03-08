# -*- coding: utf-8 -*-

{
    "name": """Odoo Cryptography Manager""",
    "summary": """Manages all sort of keys, certificates, etc.""",
    "category": "Tools",
    "images": [],
    "version": "1.1.0",
    "application": False,

    "author": "Coop. Trab. Moldeo Interactive Ltda."
              "Odoo Hrvatska"
              "DAJ M 5!",
    "support": "support@odoo-hrvatska.orgr",
    "website": "http://odoo-hrvatska.org",
    "licence": "LGPL-3",
    # "price" : 20.00,   #-> only if module if sold!
    # "currency": "EUR",

    "depends": [
        "base"
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "data": [
        "views/crypto_menuitems.xml",
        "views/generate_pairkey.xml",
        "views/generate_certificate.xml",
        "views/generate_certificate_request.xml",
        "views/pairkey_view.xml",
        "views/certificate_view.xml",
        "security/crypto_security.xml",
        "security/ir.model.access.csv",
    ],
    "qweb": [],
    "demo": [],
    "test": [
        "test/test_pairkey.yml",
        "test/test_certificate.yml"
    ],

    "auto_install": False,
    "installable": True,
}
