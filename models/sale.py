# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_affaire_id        = fields.Many2one('is.affaire', u'Machine')
    is_delai_livraison   = fields.Char(u'Délai de livraison')
    is_delai             = fields.Date(u'Date prévue de livraison')
    is_devis_id          = fields.Many2one('sale.order', u"Devis d'origine")
    is_journal_banque_id = fields.Many2one('account.journal', u'Journal de banque', domain=[('type','=','bank')])
    is_facture_proforma  = fields.Boolean(u'Facture proforma', default=False, help="Il faut cocher cette case pour imprimer la facture proforma")


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


    @api.multi
    def actualiser_affaire_sur_ligne_cde_vente_action(self):
        for obj in self:
            if obj.is_affaire_id:
                for line in obj.order_line:
                    if not line.is_affaire_id:
                        line.is_affaire_id = obj.is_affaire_id


    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res=super(SaleOrder, self).action_invoice_create()
        for id in res:
            invoices = self.env['account.invoice'].search([('id','=',id)])
            for invoice in invoices:
                for line in invoice.invoice_line_ids:
                    for sale_line in line.sale_line_ids:
                        if not line.is_affaire_id:
                            line.is_affaire_id = sale_line.is_affaire_id.id
                invoice.is_affaire_id = self.is_affaire_id.id
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_affaire_id = fields.Many2one('is.affaire', u'Machine')



