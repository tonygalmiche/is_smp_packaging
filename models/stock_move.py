# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"
    _order='date desc'

    is_affaire_id = fields.Many2one('is.affaire', u'Machine', compute='_compute_is_affaire_id', store=True, readonly=True)

    @api.depends('purchase_line_id.is_affaire_id')
    def _compute_is_affaire_id(self):
        for obj in self:
            obj.is_affaire_id = obj.purchase_line_id.is_affaire_id.id

