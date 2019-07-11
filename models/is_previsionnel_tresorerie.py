# -*- coding: utf-8 -*-
from openerp import models,fields,api
from datetime import datetime, timedelta


class is_previsionnel_tresorerie(models.Model):
    _name='is.previsionnel.tresorerie'
    _order='name'

    name       = fields.Char(u"N°previsionnel", readonly=True)
    date_debut = fields.Date(u"Date de début d'échéance", required=True)
    date_fin   = fields.Date(u"Date de fin d'échéance", required=True)
    line_ids   = fields.One2many('is.previsionnel.tresorerie.line', 'previsionnel_id', u'Lignes')



    @api.model
    def create(self, vals):
        data_obj = self.env['ir.model.data']
        sequence_ids = data_obj.search([('name','=','is_previsionnel_tresorerie_seq')])
        if sequence_ids:
            sequence_id = data_obj.browse(sequence_ids[0].id).res_id
            vals['name'] = self.env['ir.sequence'].get_id(sequence_id, 'id')
        res = super(is_previsionnel_tresorerie, self).create(vals)
        return res


    @api.multi
    def actualiser(self):
        for obj in self:
            obj.line_ids.unlink()

            #** Ajout des factures des fournisseurs ****************************
            filtre=[
                ('is_date_echeance','>=',obj.date_debut),
                ('is_date_echeance','<=',obj.date_fin),
                ('state','in',['open','paid']),
                ('type','in',['in_invoice','in_refund']),
            ]
            invoices = self.env['account.invoice'].search(filtre,order="is_date_echeance")
            for invoice in invoices:
                for line in invoice.invoice_line_ids:
                    vals={
                        'previsionnel_id': obj.id,
                        'type_od'        : 'Facture',
                        'invoice_id'     : invoice.id,
                        'date_echeance'  : invoice.is_date_echeance,
                        'partner_id'     : invoice.partner_id.id,
                        'product_id'     : line.product_id.id,
                        'qt_fac'         : line.quantity,
                        'montant'        : line.price_subtotal,
                    }
                    res=self.env['is.previsionnel.tresorerie.line'].create(vals)
            #*******************************************************************


            #** Ajout des commandes des fournisseurs ***************************
            filtre=[
                ('is_delai','<=',obj.date_fin),
                #('is_delai','<=',obj.date_fin),
                ('state','in',['purchase']),
            ]
            orders = self.env['purchase.order'].search(filtre,order="is_delai")
            for order in orders:
                date_rcp      = datetime.strptime(order.is_delai, '%Y-%m-%d')
                date_echeance = date_rcp + timedelta(days=45)
                date_echeance = date_echeance.strftime('%Y-%m-%d')
                if date_echeance>=obj.date_debut and date_echeance<=obj.date_fin:
                    for line in order.order_line:
                        if line.qty_invoiced<line.product_qty:
                            montant = (line.product_qty-line.qty_invoiced)*line.price_unit
                            vals={
                                'previsionnel_id': obj.id,
                                'type_od'        : 'Commande',
                                'order_id'       : order.id,
                                'date_prevue'    : order.is_delai,
                                'date_echeance'  : date_echeance,
                                'partner_id'     : order.partner_id.id,
                                'product_id'     : line.product_id.id,
                                'qt_cde'         : line.product_qty,
                                'qt_rcp'         : line.qty_received,
                                'qt_fac'         : line.qty_invoiced,
                                'montant'        : montant,
                            }
                            res=self.env['is.previsionnel.tresorerie.line'].create(vals)
            #*******************************************************************


    @api.multi
    def acceder_lignes(self):
        for obj in self:
            return {
                'name': "Lignes",
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'is.previsionnel.tresorerie.line',
                'type': 'ir.actions.act_window',
                'domain': [('previsionnel_id','=',obj.id)],
                'limit': 200,
            }


class is_previsionnel_tresorerie_line(models.Model):
    _name='is.previsionnel.tresorerie.line'
    _order='date_echeance,type_od,order_id,invoice_id'

    previsionnel_id = fields.Many2one('is.previsionnel.tresorerie',u'Prévionnel', required=True, ondelete='cascade')
    type_od         = fields.Selection([('Commande', u'Commande'),('Facture', u'Facture')], u"Type")
    order_id        = fields.Many2one('purchase.order', u'Commande')
    invoice_id      = fields.Many2one('account.invoice', u'Facture')
    date_prevue     = fields.Date(u"Date prévue")
    date_echeance   = fields.Date(u"Date d'échéance")
    partner_id      = fields.Many2one('res.partner', u'Partenaire')
    product_id      = fields.Many2one('product.product', u'Article')
    qt_cde          = fields.Float(u"Qt Cde")
    qt_rcp          = fields.Float(u"Qt Rcp")
    qt_fac          = fields.Float(u"Qt Fac")
    montant         = fields.Float(u"Montant HT")



