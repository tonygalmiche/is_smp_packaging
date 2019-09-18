# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_affaire_id        = fields.Many2one('is.affaire', u'Machine')
    is_delai_livraison   = fields.Char(u'Délai de livraison')
    is_devis_id          = fields.Many2one('sale.order', u"Devis d'origine")
    is_journal_banque_id = fields.Many2one('account.journal', u'Journal de banque', domain=[('type','=','bank')])


    @api.multi
    def convertir_en_commande(self):
        for obj in self:
            copy = obj.copy()
            copy.is_devis_id = obj.id
            res= {
                'name': u'Devis transformé en commande',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'res_id': copy.id,
            }
            return res

