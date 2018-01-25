# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    is_designation = fields.Text('Désignation alternative', help="Si ce champ est renseigné, cela remplacera la désignation par défaut")


