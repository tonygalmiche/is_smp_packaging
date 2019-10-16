# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools






class is_sale_order_line(models.Model):
    _name='is.sale.order.line'
    _order='date_order desc,sequence,id'
    _auto = False


    order_id                = fields.Many2one('sale.order', u'Commande')
    date_order              = fields.Date(u"Date commande")
    partner_id              = fields.Many2one('res.partner', u'Client')
    state                   = fields.Selection([
            ('draft'     , u'Devis'),
            ('sent'      , u'Devis envoyé'),
            ('sale'      , u'Commande'),
            ('done'      , u'Bloqué'),
            ('cancel'    , u'Annulée'),
        ],u"Etat commande")
    is_affaire_id           = fields.Many2one('is.affaire', u'Machine')
    sequence                = fields.Integer('Ordre')
    product_id              = fields.Many2one('product.template', 'Article')
    is_categorie_article_id = fields.Many2one('is.categorie.article', string=u'Catégorie article')
    product_uom_qty         = fields.Float(u'Qt cde'     , digits=(14,2))
    qty_delivered           = fields.Float(u'Qt livrée'  , digits=(14,2))
    qty_invoiced            = fields.Float(u'Qt facturée', digits=(14,2))
    price_unit              = fields.Float(u'Prix unitaire', digits=(14,2))
    price_subtotal          = fields.Float(u'Total HT', digits=(14,2))
    price_total             = fields.Float(u'Total TTC', digits=(14,2))


    def init(self):
        cr=self._cr
        tools.drop_view_if_exists(cr, 'is_sale_order_line')
        cr.execute("""
            CREATE OR REPLACE view is_sale_order_line AS (
                select
                    sol.id,
                    sol.order_id,
                    to_date(to_char(so.date_order,'YYYY-MM-DD'),'YYYY-MM-DD') date_order,
                    so.partner_id,
                    so.state,
                    sol.is_affaire_id,
                    sol.sequence,
                    pt.id product_id,
                    pt.is_categorie_article_id,
                    sol.product_uom_qty,
                    sol.qty_delivered,
                    sol.qty_invoiced,
                    sol.price_unit,
                    sol.price_subtotal,
                    sol.price_total
                from sale_order so inner join sale_order_line sol on so.id=sol.order_id
                                       inner join product_product      pp on sol.product_id=pp.id
                                       inner join product_template     pt on pp.product_tmpl_id=pt.id
            );
        """)

