# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    is_designation = fields.Text(u'Désignation complémentaire', help=u"Si ce champ est renseigné, cela s'ajoutera à la désignation par défaut")


