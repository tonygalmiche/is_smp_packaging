# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_affaire_id        = fields.Many2one('is.affaire', u'Machine')
    is_delai_livraison   = fields.Char(u'Délai de livraison')
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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_affaire_id = fields.Many2one('is.affaire', u'Machine')


    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )


        if self.order_id.is_affaire_id and not self.is_affaire_id:
            self.is_affaire_id = self.order_id.is_affaire_id


        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        return result
