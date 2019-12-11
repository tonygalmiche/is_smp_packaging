# -*- coding: utf-8 -*-
from openerp import models,fields,api


class is_affaire(models.Model):
    _name='is.affaire'
    _order='name'

    name              = fields.Char(u"N°machine", required=True)
    designation       = fields.Char(u"Désignation", required=True)
    location_id       = fields.Many2one('stock.location', u'Emplacement de stock', domain=[('usage','=','internal')])
    client_id         = fields.Many2one('res.partner', u'Client', domain=[('is_company','=',True),('customer','=',True)], required=True)
    code_client       = fields.Char(u'Code Client', related='client_id.is_code_client', readonly=True)
    site              = fields.Char(u"Site")
    chef_projet       = fields.Char(u"Chef de projet")
    acheteur          = fields.Char(u"Acheteur")
    commentaire       = fields.Text(u"Commentaire")
    sous_ensemble_ids = fields.One2many('is.sous.ensemble', 'affaire_id', u'Sous-ensembles', readonly=True)


    @api.model
    def create(self, vals):
        location = self._creer_emplacement_stock(vals['name'])
        vals['location_id']=location.id
        obj = super(is_affaire, self).create(vals)
        return obj


    @api.multi
    def write(self,vals):
        for obj in self:
            if 'name' in vals and obj.location_id:
                obj.location_id.name = vals['name']
        res = super(is_affaire, self).write(vals)
        return res


    @api.multi
    def _creer_emplacement_stock(self,name):
        locations = self.env['stock.location'].search([('name','=',name)])
        if len(locations):
            location = locations[0]
        else:
            vals={
                'location_id': 3, # Emplacements Virtuels
                'name'       : name,
                'usage'      : 'internal',
            }
            location = self.env['stock.location'].create(vals)
        return location


    @api.multi
    def creer_emplacement_stock_action(self):
        for obj in self:
            if not obj.location_id:
                location = self._creer_emplacement_stock(obj.name)
                obj.location_id = location.id
