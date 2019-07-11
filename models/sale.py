# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_affaire_id      = fields.Many2one('is.affaire', u'Machine')
    is_delai_livraison = fields.Char(u'Délai de livraison')

