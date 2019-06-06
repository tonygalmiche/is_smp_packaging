# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"

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


