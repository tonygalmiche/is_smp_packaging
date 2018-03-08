# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class is_profession(models.Model):
    _name='is.profession'
    _order='name'

    name = fields.Char("Profession", required=True)
    code = fields.Char("Code")


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_code_client      = fields.Char('Code Client')
    is_code_fournisseur = fields.Char('Code Fournisseur')
    is_contact          = fields.Char('Contact')
    is_profession_id    = fields.Many2one('is.profession', 'Profession')
    is_num_compte       = fields.Char('N°Compte')
    is_information      = fields.Char('Informations')



