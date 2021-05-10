# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class is_account_invoice_line(models.Model):
    _name='is.account.invoice.line'
    _order='invoice_id desc, id'
    _auto = False


    @api.depends('price_unit')
    def _compute(self):
        for obj in self:
            obj.cout_total = obj.standard_price*obj.quantity
            obj.marge      = (obj.price_unit-obj.standard_price)*obj.quantity


    invoice_id             = fields.Many2one('account.invoice', u'Facture')
    number                 = fields.Char(u"N°Facture")
    date_invoice           = fields.Date(u"Date Facture")
    date_due               = fields.Date(u"Date Echéance")
    product_id             = fields.Many2one('product.product', u'Article')
    description            = fields.Text(u"Description")
    is_affaire_id          = fields.Many2one('is.affaire', u'Machine')
    quantity               = fields.Float(u'Quantité'   , digits=(14,2))
    price_unit             = fields.Float(u'Prix unitaire', digits=(14,4))
    price_subtotal         = fields.Float(u'Montant HT'   , digits=(14,4))
    partner_id             = fields.Many2one('res.partner', u'Client/Fournisseur Facturé')
    type                   = fields.Char(u"Type Facture")
    state                  = fields.Char(u"Etat Facture")
    standard_price         = fields.Float(u'Coût unitaire', related='product_id.standard_price', readonly=True)
    cout_total             = fields.Float(u'Coût total'  , digits=(14,4), compute='_compute', store=False, readonly=True)
    marge                  = fields.Float(u'Marge totale', digits=(14,4), compute='_compute', store=False, readonly=True)


    def init(self):
        cr=self._cr
        tools.drop_view_if_exists(cr, 'is_account_invoice_line')
        cr.execute("""
            CREATE OR REPLACE view is_account_invoice_line AS (
                select
                    ail.id,
                    ail.invoice_id,
                    ai.number,
                    ai.date_invoice,
                    ai.date_due,
                    ail.product_id,
                    ail.name description,
                    ail.is_affaire_id,
                    ail.quantity,
                    ail.price_unit,
                    ail.price_subtotal,
                    ai.partner_id,
                    ai.type,
                    ai.state
                from account_invoice_line ail inner join account_invoice   ai on ail.invoice_id=ai.id
                                               left join product_product   pp on ail.product_id=pp.id
                                               inner join product_template pt on pp.product_tmpl_id=pt.id
            );
        """)

