# -*- coding: utf-8 -*-
{
    'name'     : 'InfoSaône - Module Odoo pour SMP Packaging',
    'version'  : '0.1',
    'author'   : 'InfoSaône',
    'category' : 'InfoSaône',


    'description': """
InfoSaône - Module Odoo pour SMP Packaging
===================================================
""",
    'maintainer' : 'InfoSaône',
    'website'    : 'http://www.infosaone.com',
    'depends'    : [
        'base',
        'account',
        'account_accountant',
        'document',
],
    'data' : [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/is_export_compta_view.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': [
    ],
}

