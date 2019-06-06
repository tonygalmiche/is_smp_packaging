# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class is_profession(models.Model):
    _name='is.profession'
    _order='name'

    name = fields.Char(u"Profession", required=True)
    code = fields.Char(u"Code")


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_code_client      = fields.Char(u'Code Client')
    is_code_fournisseur = fields.Char(u'Code Fournisseur')
    is_contact          = fields.Char(u'Contact')
    is_profession_id    = fields.Many2one('is.profession', u'Profession')
    is_num_compte       = fields.Char(u'N°Compte')
    is_information      = fields.Char(u'Informations')



