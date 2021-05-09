# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"
    _order='id desc'

    is_date_prevue      = fields.Date(u'Date prévue de livraison', compute='_compute', store=True, readonly=True)
    is_date_bl          = fields.Date(u'Date du BL')
    is_conditionnement  = fields.Char(u'Conditionnement')
    is_longueur         = fields.Float(u'Longueur (cm)', digits=(16, 2))
    is_largeur          = fields.Float(u'Largeur (cm)' , digits=(16, 2))
    is_hauteur          = fields.Float(u'Hauteur (cm)' , digits=(16, 2))
    is_poids            = fields.Float(u'Poids (kg)'   , digits=(16, 3))
    is_description_haut = fields.Text(u'Description haute (jaune)')
    is_description_bas  = fields.Text(u'Description bas')
    is_signature        = fields.Boolean(u'Signature direction', help=u"Ajouter la signature de la direction sur le BL")
    is_tampon           = fields.Boolean(u'Tampon direction'   , help=u"Ajouter le tampon avec la signature de la direction sur le BL")
    is_affaire_id       = fields.Many2one('is.affaire', u'Machine', compute='_compute_is_affaire_id', store=True, readonly=True)


    @api.depends('purchase_id','sale_id')
    def _compute_is_affaire_id(self):
        for obj in self:
            affaire_id=False
            if obj.sale_id:
                affaire_id = obj.sale_id.is_affaire_id
            if obj.purchase_id:
                affaire_id = obj.purchase_id.is_affaire_id

            obj.is_affaire_id = affaire_id


    @api.depends('purchase_id.is_delai','sale_id.is_delai','state')
    def _compute(self):
        for obj in self:
            if obj.picking_type_id.id==1:
                obj.is_date_prevue = obj.purchase_id.is_delai
            else:
                obj.is_date_prevue = obj.sale_id.is_delai


    def move2affaire(self):
        """Mettre les articles en réception dans l'emplacement de l'affaire"""
        if self.picking_type_id.id==1:
            for move in self.move_lines:
                if move.purchase_line_id.is_affaire_id.location_id.id:
                    vals={
                        'product_id'      : move.product_id.id,
                        'product_uom_qty' : move.product_uom_qty,
                        'product_uom'     : move.product_uom.id,
                        'name'            : move.name,
                        'origin'          : move.origin,
                        'location_id'     : move.location_dest_id.id,
                        'location_dest_id': move.purchase_line_id.is_affaire_id.location_id.id,
                        #'purchase_line_id': move.purchase_line_id.id, # TODO Ne pas mettre cette ligne, car cela duplique les quantités réceptionnées dans la commande
                        #'is_affaire_id'   : move.is_affaire_id.id,
                    }
                    new = self.env['stock.move'].create(vals)
                    new.action_confirm()
                    new.action_done()
        # **********************************************************************


    @api.multi
    def initialiser_date_prevue_action(self):
        for obj in self:
            if not obj.is_date_prevue:
                if obj.picking_type_id.id==1:
                    obj.is_date_prevue = obj.purchase_id.is_delai
                else:
                    print obj,obj.sale_id,obj.sale_id.is_delai
                    obj.is_date_prevue = obj.sale_id.is_delai







class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    @api.one
    def _process(self, cancel_backorder=False):
        res = super(StockBackorderConfirmation, self)._process()
        self.pick_id.move2affaire()


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    @api.multi
    def process(self):
        res = super(StockImmediateTransfer, self).process()
        self.pick_id.move2affaire()
        return res


