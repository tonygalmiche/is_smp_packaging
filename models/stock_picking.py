# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"

    is_date_bl          = fields.Date('Date du BL')
    is_conditionnement  = fields.Char('Conditionnement')
    is_longueur         = fields.Float('Longueur (cm)', digits=(16, 2))
    is_largeur          = fields.Float('Largeur (cm)' , digits=(16, 2))
    is_hauteur          = fields.Float('Hauteur (cm)' , digits=(16, 2))
    is_poids            = fields.Float('Poids (kg)'   , digits=(16, 3))
    is_description_haut = fields.Text('Description haute (jaune)')
    is_description_bas  = fields.Text('Description bas')
    is_signature        = fields.Boolean('Signature direction', help="Ajouter la signature de la direction sur le BL")


