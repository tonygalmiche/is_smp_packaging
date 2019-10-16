# -*- coding: utf-8 -*-
from openerp import models,fields,api
import tempfile
import base64
import os
import csv
import codecs
import datetime


class is_sous_ensemble(models.Model):
    _name='is.sous.ensemble'
    _order='name desc'

    name        = fields.Char(u"Référence", required=True)
    affaire_id  = fields.Many2one('is.affaire', u'Affaire')
    designation = fields.Text(u"Désignation")


    @api.multi
    def acceder_sous_ensemble(self):
        for obj in self:
            return {
                'name': u'Sous-ensemble '+obj.name or '',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_model': 'is.sous.ensemble',
                'res_id': obj.id,
                'type': 'ir.actions.act_window',
            }


    @api.multi
    def acceder_lignes(self):
        for obj in self:
            return {
                'name': "Lignes",
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'is.sous.ensemble.line',
                'type': 'ir.actions.act_window',
                'domain': [('sous_ensemble_id','=',obj.id)],
                'limit': 200,
            }


    @api.multi
    def importer_nomenclature(self):
        for obj in self:
            # ** Recherche si une pièce jointe est déja associèe ***************
            attachment_obj = self.env['ir.attachment']
            model=self._name
            attachments = attachment_obj.search([('res_model','=',model),('res_id','=',obj.id)],order="id desc",limit=1)
            # ******************************************************************

            for attachment in attachments:
                csvfile = base64.decodestring(attachment.datas)
                csvfile = csvfile.split("\n")
                csvfile = csv.reader(csvfile, delimiter=';')
                line_obj    = self.env['is.sous.ensemble.line']
                product_obj = self.env['product.product']
                for ct, line in enumerate(csvfile):
                    ordre=ct+1
                    if len(line)>6:
                        quantite=0
                        try:
                            quantite = float(line[5])
                        except ValueError:
                            continue
                        if quantite>0:
                            filtre=[
                                ('affaire_id'      , '=', obj.affaire_id.id),
                                ('sous_ensemble_id', '=', obj.id),
                                ('ordre'           , '=', ordre),
                            ]
                            lines = line_obj.search(filtre,order="id desc",limit=1)
                            if len(lines)==0:

                                #** Recherche categorie ************************
                                cat = unicode(line[6].strip(),'utf-8')
                                categories = self.env['is.categorie.article'].search([('name','=',cat)],order="id desc",limit=1)
                                anomalies=[]
                                categorie_article_id = False
                                account_expense_id = False
                                if categories:
                                    categorie_article_id = categories[0].id
                                    account_expense_id = categories[0].account_expense_id.id
                                else:
                                    anomalies.append(u"Catégorie article '"+cat+u"' inconnue")
                                #***************************************************


                                #** Recherche matière **************************
                                matiere_id = False
                                mat = unicode(line[2].strip(),'utf-8')
                                if mat!='':
                                    matieres = self.env['is.matiere'].search([('name','=',mat)],order="id desc",limit=1)
                                    if matieres:
                                        matiere_id = matieres[0].id
                                    else:
                                        anomalies.append(u"Matière '"+mat+u"' inconnue")
                                        #anomalies.append(mat)
                                #***************************************************


                                creation_product=True
                                products = product_obj.search([('default_code','=',line[1])],order="id desc",limit=1)
                                if len(products)>0:
                                    product=products[0]
                                    creation_product=False
                                if creation_product:
                                    vals={
                                        'default_code' : line[1],
                                        'name'         : unicode(line[4],'utf-8'),
                                        'is_fabriquant' : line[3],
                                        'is_categorie_article_id' :categorie_article_id,
                                        'is_matiere_id': matiere_id,
                                        'type'         : 'product',
                                        'list_price'   : 0,
                                        'property_account_expense_id': account_expense_id,
                                    }
                                    product=product_obj.create(vals)
                                vals={
                                    'affaire_id'          : obj.affaire_id.id,
                                    'sous_ensemble_id'    : obj.id,
                                    'ordre'               : ordre,
                                    'product_id'          : product.id,
                                    'reference'           : product.default_code,
                                    'designation'         : product.name,
                                    'creation_product'    : creation_product,
                                    'matiere_id'          : matiere_id,
                                    'fabriquant'          : line[3],
                                    'quantite'            : line[5],
                                    'categorie_article_id': categorie_article_id,
                                    'anomalie'            : ', '.join(anomalies),
                                }
                                line=line_obj.create(vals)
                                line.actualiser()
                return self.acceder_lignes()


class is_sous_ensemble_line(models.Model):
    _name='is.sous.ensemble.line'
    _order='affaire_id,sous_ensemble_id,ordre,product_id'
    _rec_name='product_id'


    affaire_id           = fields.Many2one('is.affaire',u'Affaire', required=True)
    sous_ensemble_id     = fields.Many2one('is.sous.ensemble', u'Sous-ensemble', required=True)
    ordre                = fields.Integer(u"Ligne")
    product_id           = fields.Many2one('product.product', u'[Référence] Désignation', domain=[('purchase_ok', '=', True)])
    reference            = fields.Char(u'Référence', readonly=True)
    designation          = fields.Char(u'Désignation', readonly=True)
    creation_product     = fields.Boolean(u"Création",help=u"Indique si l'article a été créé lors de l'importation",readonly=True)
    matiere_id           = fields.Many2one('is.matiere', u'Matière')
    fabriquant           = fields.Char(u"Fabriquant")
    quantite             = fields.Integer(u"Quantité")
    categorie_article_id = fields.Many2one('is.categorie.article', u'Catégorie')
    suivi_par_id         = fields.Many2one('res.users', u'Suivi par')
    order_id             = fields.Many2one('purchase.order', u'N°Cde')
    date_cde             = fields.Date(u"Date Cde")
    delai                = fields.Date(u"Délai")
    recu_le              = fields.Date(u"Reçu le")
    code                 = fields.Char(u"Code Fournisseur")
    fournisseur_id       = fields.Many2one('res.partner', u'Fournisseur', domain=[('is_company','=',True),('supplier','=',True)])
    ref_fournisseur      = fields.Char(u"Réf fournisseur")
    pu_ht                = fields.Float(u"PU HT")
    total_ht             = fields.Float(u"Total HT")
    order_ids            = fields.Many2many('purchase.order', 'is_sous_ensemble_line_order_rel', 'line_id','order_id', string=u"Devis")
    order_nb             = fields.Integer(u"Nb devis")
    anomalie             = fields.Char(u"Anomalie")
    order_line_ids       = fields.One2many('is.sous.ensemble.line.order', 'line_id', u'Lignes de commandes', readonly=True)


    @api.multi
    def creer_devis_action(self):
        affaire_id = False
        for obj in self:
            affaire_id=obj.affaire_id.id
        user = self.env['res.users'].search([('id','=',self._uid)],limit=1)[0]
        partner = user.partner_id
        vals={
            'partner_id'        : partner.id,
            'is_affaire_id'     : affaire_id,
            'fiscal_position_id': partner.property_account_position_id.id,
        }
        order=self.env['purchase.order'].create(vals)
        if order:
            order_line_obj = self.env['purchase.order.line']
            for obj in self:
                now = datetime.date.today()
                date_planned = now.strftime('%Y-%m-%d')
                obj.suivi_par_id = self._uid
                taxes_id=[]
                for tax in obj.product_id.supplier_taxes_id:
                    taxes_id.append(tax.id)
                vals={
                    'order_id'      : order.id,
                    'product_id'    : obj.product_id.id,
                    'name'          : obj.product_id.name,
                    'is_affaire_id' : affaire_id,
                    'product_uom'   : obj.product_id.uom_id.id ,
                    'price_unit'    : 0,
                    'product_qty'   : obj.quantite,
                    'date_planned'  : date_planned,
                    'taxes_id'      : [(6,0,taxes_id)],
                }
                line=order_line_obj.create(vals)
                obj.actualiser()


    @api.multi
    def actualiser_ligne_scheduler_action(self):
        self.env['is.sous.ensemble.line'].search([]).actualiser_ligne_action()


    @api.multi
    def actualiser_ligne_action(self):
        nb=len(self)
        ct=0
        for obj in self:
            ct+=1
            obj.actualiser()


    @api.multi
    def actualiser(self):
        for obj in self:
            obj.order_line_ids.unlink()

            obj.reference            = obj.product_id.default_code
            obj.designation          = obj.product_id.name
            obj.matiere_id           = obj.product_id.is_matiere_id
            obj.fabriquant           = obj.product_id.is_fabriquant
            obj.categorie_article_id = obj.product_id.is_categorie_article_id


            lines = self.env['purchase.order.line'].search([('product_id','=',obj.product_id.id)],order="id desc",limit=20)
            nb=0
            for line in lines:
                nb+=1
                vals={
                    'affaire_id'      : obj.affaire_id.id,
                    'sous_ensemble_id': obj.sous_ensemble_id.id,
                    'line_id'         : obj.id,
                    'order_id'        : line.order_id.id,
                    'partner_id'      : line.partner_id.id,
                    'product_id'      : line.product_id.id,
                    'quantite'        : line.product_qty,
                    'prix'            : line.price_unit,
                    'state'           : line.order_id.state,
                }
                if line.order_id.state=='purchase' and line.order_id.is_affaire_id==obj.affaire_id:
                    obj.order_id        = line.order_id.id
                    obj.date_cde        = line.order_id.date_order
                    obj.delai           = line.order_id.is_delai
                    obj.code            = line.order_id.partner_id.is_code_fournisseur
                    obj.fournisseur_id  = line.order_id.partner_id.id
                    obj.ref_fournisseur = line.order_id.is_devis
                    obj.pu_ht           = line.price_unit
                    obj.total_ht        = line.price_subtotal
                    for move in line.move_ids:
                        if move.state=='done':
                            obj.recu_le=move.date


                line=self.env['is.sous.ensemble.line.order'].create(vals)
            obj.order_nb = nb

class is_sous_ensemble_line_order(models.Model):
    _name='is.sous.ensemble.line.order'

    affaire_id           = fields.Many2one('is.affaire',u'Affaire', required=True)
    sous_ensemble_id     = fields.Many2one('is.sous.ensemble', u'Sous-ensemble', required=True)
    line_id              = fields.Many2one('is.sous.ensemble.line', u'Ligne', required=True, ondelete='cascade')
    order_id             = fields.Many2one('purchase.order', u'Commande')
    partner_id           = fields.Many2one('res.partner', u'Fournisseur')
    product_id           = fields.Many2one('product.product', u'Référence')
    quantite             = fields.Float(u"Quantité")
    prix                 = fields.Float(u"PU HT")
    state                = fields.Char(u"Etat")






