# -*- coding: utf-8 -*-
from openerp import models,fields,api


class is_affaire(models.Model):
    _name='is.affaire'
    _order='client_id,name'

    name        = fields.Char("N°affaire", required=True)
    designation = fields.Char("Désignation", required=True)
    client_id   = fields.Many2one('res.partner', 'Client', domain=[('is_company','=',True),('customer','=',True)], required=True)
    code_client = fields.Char('Code Client', related='client_id.is_code_client', readonly=True)
    site        = fields.Char("Site")
    chef_projet = fields.Char("Chef de projet")
    acheteur    = fields.Char("Acheteur")
    commentaire = fields.Text("Commentaire")




