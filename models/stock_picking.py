# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"

    is_conditionnement = fields.Char('Conditionnement')
    is_longueur        = fields.Float('Longueur (cm)')
    is_largeur         = fields.Float('Largeur (cm)')
    is_hauteur         = fields.Float('Hauteur (cm)')
    is_poids           = fields.Float('Poids (kg)')
    is_description_bas = fields.Text('Description bas')


