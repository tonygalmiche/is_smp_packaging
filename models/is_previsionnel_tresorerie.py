# -*- coding: utf-8 -*-
from openerp import models,fields,api
from datetime import datetime, timedelta


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)


class is_previsionnel_tresorerie(models.Model):
    _name='is.previsionnel.tresorerie'
    _order='name desc'

    name         = fields.Char(u"N°previsionnel", readonly=True)
    suivi_par_id = fields.Many2one('res.users', u'Suivi par', default=lambda self: self.env.uid)
    date_debut   = fields.Date(u"Date de début d'échéance", required=True)
    date_fin     = fields.Date(u"Date de fin d'échéance", required=True)
    line_ids     = fields.One2many('is.previsionnel.tresorerie.line', 'previsionnel_id', u'Lignes')


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
                    tva = 0.0
                    for tax in line.invoice_line_tax_ids:
                        tva = tva + line.price_subtotal*abs(tax.amount)/100.0
                    vals={
                        'previsionnel_id': obj.id,
                        'type_od'        : 'Facture',
                        'invoice_id'     : invoice.id,
                        'affaire_id'     : line.is_affaire_id.id,
                        'date_echeance'  : invoice.is_date_echeance,
                        'partner_id'     : invoice.partner_id.id,
                        'product_id'     : line.product_id.id,
                        'qt_fac'         : line.quantity,
                        'montant'        : line.price_subtotal,
                        'montant_ttc'    : line.price_subtotal + tva,
                    }
                    res=self.env['is.previsionnel.tresorerie.line'].create(vals)
            #*******************************************************************


            #** Ajout des commandes des fournisseurs non réceptionées **********
            filtre=[
                ('state','in',['purchase']),
            ]
            orders = self.env['purchase.order'].search(filtre,order="is_delai")
            for order in orders:
                if order.is_delai:
                    date_rcp      = datetime.strptime(order.is_delai, '%Y-%m-%d')
                    date_echeance = last_day_of_month(date_rcp) + timedelta(days=1)
                    date_echeance = last_day_of_month(date_echeance)
                    date_echeance = date_echeance + timedelta(days=15)
                    date_echeance = date_echeance.strftime('%Y-%m-%d')
                    if date_echeance>=obj.date_debut and date_echeance<=obj.date_fin:
                        for line in order.order_line:
                            if line.qty_received<line.product_qty:
                                montant = (line.product_qty-line.qty_received)*line.price_unit
                                tva = 0.0
                                for tax in line.taxes_id:
                                    tva = tva + (line.product_qty-line.qty_received)*line.price_unit*abs(tax.amount)/100.0
                                vals={
                                    'previsionnel_id': obj.id,
                                    'type_od'        : 'Commande',
                                    'order_id'       : order.id,
                                    'affaire_id'     : line.is_affaire_id.id,
                                    'date_prevue'    : order.is_delai,
                                    'date_echeance'  : date_echeance,
                                    'partner_id'     : order.partner_id.id,
                                    'product_id'     : line.product_id.id,
                                    'qt_cde'         : line.product_qty,
                                    'qt_rcp'         : line.qty_received,
                                    'qt_fac'         : line.qty_invoiced,
                                    'montant'        : montant,
                                    'montant_ttc'    : montant + tva,
                                }
                                res=self.env['is.previsionnel.tresorerie.line'].create(vals)
            #*******************************************************************


            #** Ajout des réceptions des fournisseurs **************************
            filtre=[
                ('state','in',['purchase']),
            ]
            orders = self.env['purchase.order'].search(filtre,order="is_delai")
            for order in orders:
                if order.is_delai:
                    for line in order.order_line:
                        date_bl = False
                        for move in line.move_ids:
                            date_bl = move.picking_id.is_date_bl
                            if not date_bl:
                                date_bl = datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S')
                            else:
                                date_bl = datetime.strptime(date_bl, '%Y-%m-%d')
                        if date_bl:
                            date_echeance = last_day_of_month(date_bl) + timedelta(days=1)
                            date_echeance = last_day_of_month(date_echeance)
                            date_echeance = date_echeance + timedelta(days=15)
                            date_echeance = date_echeance.strftime('%Y-%m-%d')
                            if date_echeance>=obj.date_debut and date_echeance<=obj.date_fin:
                                if line.qty_invoiced<line.qty_received:
                                    montant = (line.qty_received-line.qty_invoiced)*line.price_unit
                                    tva = 0.0
                                    for tax in line.taxes_id:
                                        tva = tva + (line.qty_received-line.qty_invoiced)*line.price_unit*abs(tax.amount)/100.0
                                    vals={
                                        'previsionnel_id': obj.id,
                                        'type_od'        : u'Réception',
                                        'order_id'       : order.id,
                                        'affaire_id'     : line.is_affaire_id.id,
                                        'date_prevue'    : date_bl,
                                        'date_echeance'  : date_echeance,
                                        'partner_id'     : order.partner_id.id,
                                        'product_id'     : line.product_id.id,
                                        'qt_cde'         : line.product_qty,
                                        'qt_rcp'         : line.qty_received,
                                        'qt_fac'         : line.qty_invoiced,
                                        'montant'        : montant,
                                        'montant_ttc'    : montant + tva,
                                    }
                                    res=self.env['is.previsionnel.tresorerie.line'].create(vals)
            #*******************************************************************


    @api.multi
    def acceder_lignes(self):
        for obj in self:
            return {
                'name': "Lignes",
                'view_mode': 'tree,form,graph,pivot',
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
    type_od         = fields.Selection([('Commande', u'Commande'),(u'Réception', u'Réception'),('Facture', u'Facture')], u"Type")
    order_id        = fields.Many2one('purchase.order', u'Commande')
    invoice_id      = fields.Many2one('account.invoice', u'Facture')
    affaire_id      = fields.Many2one('is.affaire', u'Machine')
    date_prevue     = fields.Date(u"Date prévue")
    date_echeance   = fields.Date(u"Date d'échéance")
    partner_id      = fields.Many2one('res.partner', u'Partenaire')
    product_id      = fields.Many2one('product.product', u'Article')
    qt_cde          = fields.Float(u"Qt Cde")
    qt_rcp          = fields.Float(u"Qt Rcp")
    qt_fac          = fields.Float(u"Qt Fac")
    montant         = fields.Float(u"Montant HT")
    montant_ttc     = fields.Float(u"Montant TTC")


