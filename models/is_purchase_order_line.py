# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class is_purchase_order_line(models.Model):
    _name='is.purchase.order.line'
    _order='date_order desc,sequence,id'
    _auto = False

    order_id                = fields.Many2one('purchase.order', u'Commande')
    date_order              = fields.Date(u"Date commande")
    partner_id              = fields.Many2one('res.partner', u'Fournisseur')
    state                   = fields.Char(u"Etat commande")
    invoice_status          = fields.Char(u"Etat facturation")
    is_affaire_id           = fields.Many2one('is.affaire', u'Machine')
    sequence                = fields.Integer('Ordre')
    product_id              = fields.Many2one('product.template', 'Article')
    is_categorie_article_id = fields.Many2one('is.categorie.article', string=u'Catégorie article')
    product_uom             = fields.Many2one('product.uom', u'Unité')
    product_qty             = fields.Float(u'Qt cde'     , digits=(14,2))
    qty_received            = fields.Float(u'Qt reçue'   , digits=(14,2))
    qty_invoiced            = fields.Float(u'Qt facturée', digits=(14,2))
    price_unit              = fields.Float(u'Prix unitaire', digits=(14,2))
    price_subtotal          = fields.Float(u'Total HT', digits=(14,2))
    price_total             = fields.Float(u'Total TTC', digits=(14,2))
    date_planned            = fields.Date(u"Date prévue")


# to_char(aff_date_creation,'YYYY')='[m

    def init(self):
        cr=self._cr
        tools.drop_view_if_exists(cr, 'is_purchase_order_line')
        cr.execute("""
            CREATE OR REPLACE view is_purchase_order_line AS (
                select
                    pol.id,
                    pol.order_id,
                    to_date(to_char(po.date_order,'YYYY-MM-DD'),'YYYY-MM-DD') date_order,
                    po.partner_id,
                    po.state,
                    po.invoice_status,
                    po.is_affaire_id,
                    pol.sequence,
                    pt.id product_id,
                    pt.is_categorie_article_id,
                    pol.product_uom,
                    pol.product_qty,
                    pol.qty_received,
                    pol.qty_invoiced,
                    pol.price_unit,
                    pol.price_subtotal,
                    pol.price_total,
                    to_date(to_char(pol.date_planned,'YYYY-MM-DD'),'YYYY-MM-DD') date_planned
                from purchase_order po inner join purchase_order_line pol on po.id=pol.order_id
                                       inner join product_product      pp on pol.product_id=pp.id
                                       inner join product_template     pt on pp.product_tmpl_id=pt.id
            );
        """)

