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

        'views/account_invoice_view.xml',
        'views/partner_view.xml',
        'views/stock_picking_views.xml',
        'report/report_invoice.xml',
        'report/report_deliveryslip.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': [
    ],
}

