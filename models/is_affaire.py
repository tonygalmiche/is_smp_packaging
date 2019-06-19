# -*- coding: utf-8 -*-
from openerp import models,fields,api


class is_affaire(models.Model):
    _name='is.affaire'
    _order='name'

    name              = fields.Char(u"N°machine", required=True)
    designation       = fields.Char(u"Désignation", required=True)
    client_id         = fields.Many2one('res.partner', u'Client', domain=[('is_company','=',True),('customer','=',True)], required=True)
    code_client       = fields.Char(u'Code Client', related='client_id.is_code_client', readonly=True)
    site              = fields.Char(u"Site")
    chef_projet       = fields.Char(u"Chef de projet")
    acheteur          = fields.Char(u"Acheteur")
    commentaire       = fields.Text(u"Commentaire")
    sous_ensemble_ids = fields.One2many('is.sous.ensemble', 'affaire_id', u'Sous-ensembles', readonly=True)



