# -*- coding: utf-8 -*-
{
    'name'     : 'InfoSaône - Module Odoo pour SMP Packaging',
    'version'  : '0.1',
    'author'   : u'InfoSaône',
    'category' : u'InfoSaône',
    'description': """
InfoSaône - Module Odoo pour SMP Packaging
===================================================
""",
    'maintainer' : 'InfoSaône',
    'website'    : 'http://www.infosaone.com',
    'depends'    : [
        'base',
        'sale',
        'purchase',
        'account',
        'account_accountant',
        'document',
],
    'data' : [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/product_view.xml',
        'views/purchase_view.xml',
        'views/is_export_compta_view.xml',
        'views/account_invoice_view.xml',
        'views/partner_view.xml',
        'views/stock_picking_views.xml',
        'views/sale_view.xml',
        'views/is_affaire_view.xml',
        'views/account_view.xml',
        'views/is_purchase_order_line.xml',
        'views/is_account_invoice_line.xml',
        'views/is_sous_ensemble_view.xml',
        'views/is_previsionnel_tresorerie_view.xml',
        'views/menu.xml',
        'report/report_invoice.xml',
        'report/report_deliveryslip.xml',
        'report/purchase_quotation_templates.xml',
        'report/purchase_order_templates.xml',
        'report/sale_report_templates.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': [
    ],
}

