# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_code_client      = fields.Char('Code Client')
    is_code_fournisseur = fields.Char('Code Fournisseur')


