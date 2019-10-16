# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_devis      = fields.Char(u'Devis n°')
    is_delai      = fields.Date(u'Date prévue de livraison')
    is_affaire_id = fields.Many2one('is.affaire', u'Machine')
    is_devis_id   = fields.Many2one('purchase.order', u"Devis d'origine",domain=[('state', '=', ['draft','sent','to_approve'])],)


    @api.multi
    def forcer_commande_achat_non_facturable_action(self):
        for obj in self:
            if obj.invoice_status=='to invoice':
                obj.invoice_status='no'


    @api.multi
    def forcer_commande_achat_facturable_action(self):
        for obj in self:
            if obj.invoice_status=='no':
                obj.invoice_status='to invoice'



    @api.multi
    def convertir_en_commande(self):
        for obj in self:
            copy = obj.copy()
            copy.is_devis_id = obj.id
            res= {
                'name': u'Devis transformé en commande',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                'res_id': copy.id,
            }
            return res


    @api.multi
    def acceder_devis(self):
        for obj in self:
            return {
                'name': u'Devis '+obj.name or '',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_model': 'purchase.order',
                'res_id': obj.id,
                'type': 'ir.actions.act_window',
            }


    @api.multi
    def actualiser_affaire_sur_ligne_cde_action(self):
        for obj in self:
            if obj.is_affaire_id:
                for line in obj.order_line:
                    if not line.is_affaire_id:
                        line.is_affaire_id = obj.is_affaire_id
                    if not line.taxes_id:
                        taxes_id=[]
                        for tax in line.product_id.supplier_taxes_id:
                            taxes_id.append(tax.id)
                        vals={
                            'taxes_id': [(6,0,taxes_id)],
                        }
                        line.write(vals)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    is_affaire_id = fields.Many2one('is.affaire', u'Machine')


    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })

        #self.name = product_lang.display_name
        #if product_lang.description_purchase:
        #    self.name += '\n' + product_lang.description_purchase

        self.name = product_lang.name


        if self.order_id.is_affaire_id and not self.is_affaire_id:
            self.is_affaire_id = self.order_id.is_affaire_id


        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

        self._suggest_quantity()
        self._onchange_quantity()

        return result




