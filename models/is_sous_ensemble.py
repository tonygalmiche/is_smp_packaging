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
                                cat = line[6]
                                categories = self.env['is.categorie.article'].search([('name','=',cat)],order="id desc",limit=1)
                                anomalies=[]
                                categorie_article_id = False
                                account_expense_id = False
                                if categories:
                                    categorie_article_id = categories[0].id
                                    account_expense_id = categories[0].account_expense_id.id
                                else:
                                    anomalies.append(u"Catégorie article '"+str(cat)+u"' inconnue")
                                #***************************************************


                                #** Recherche matière **************************
                                matiere_id = False
                                mat = line[2].strip()
                                if mat!='':
                                    matieres = self.env['is.matiere'].search([('name','=',mat)],order="id desc",limit=1)
                                    if matieres:
                                        matiere_id = matieres[0].id
                                    else:
                                        anomalies.append(u"Matière article '"+str(mat)+u"' inconnue")
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
                                    'creation_product'    : creation_product,
                                    'matiere_id'          : matiere_id,
                                    'fabriquant'          : line[3],
                                    'quantite'            : line[5],
                                    'categorie_article_id': categorie_article_id,
                                    'anomalie'            : ', '.join(anomalies),
                                }
                                res=line_obj.create(vals)
                return self.acceder_lignes()


class is_sous_ensemble_line(models.Model):
    _name='is.sous.ensemble.line'
    _order='affaire_id,sous_ensemble_id,ordre,product_id'
    _rec_name='product_id'


    affaire_id           = fields.Many2one('is.affaire',u'Affaire', required=True)
    sous_ensemble_id     = fields.Many2one('is.sous.ensemble', u'Sous-ensemble', required=True)
    ordre                = fields.Integer(u"Ligne")
    product_id           = fields.Many2one('product.product', u'Référence', domain=[('purchase_ok', '=', True)])
    creation_product     = fields.Boolean(u"Création",help=u"Indique si l'article a été créé lors de l'importation",readonly=True)
    matiere_id           = fields.Many2one('is.matiere', u'Matière')
    fabriquant           = fields.Char(u"Fabriquant")
    quantite             = fields.Integer(u"Quantité")
    categorie_article_id = fields.Many2one('is.categorie.article', u'Catégorie')
    suivi_par_id         = fields.Many2one('res.users', u'Suivi par')
    num_cde              = fields.Char(u"N°Cde")
    date_cde             = fields.Date(u"Date Cde")
    delai                = fields.Date(u"Délai")
    recu_le              = fields.Date(u"Reçu le")
    code                 = fields.Char(u"Code")
    fournisseur_id       = fields.Many2one('res.partner', u'Fournisseur', domain=[('is_company','=',True),('supplier','=',True)])
    ref_fournisseur      = fields.Char(u"Réf fournisseur")
    pu_ht                = fields.Float(u"PU HT")
    total_ht             = fields.Float(u"Total HT")
    order_ids            = fields.Many2many('purchase.order', 'is_sous_ensemble_line_order_rel', 'line_id','order_id', string=u"Devis")
    anomalie             = fields.Char(u"Anomalie")


    @api.multi
    def creer_devis_action(self):
        partner=self.env['res.partner'].search([],limit=1)[0]
        vals={
            'partner_id'      : partner.id,
            'fiscal_position_id' : partner.property_account_position_id.id,
        }
        order=self.env['purchase.order'].create(vals)
        if order:
            order_line_obj = self.env['purchase.order.line']
            for obj in self:
                now = datetime.date.today()
                date_planned = now.strftime('%Y-%m-%d')
                obj.suivi_par_id = self._uid
                vals={
                    'order_id'    : order.id,
                    'product_id'  : obj.product_id.id,
                    'name'        : obj.product_id.name,
                    'product_uom' : obj.product_id.uom_id.id ,
                    'price_unit'  : 0,
                    'product_qty' : obj.quantite,
                    'date_planned': date_planned,
                }
                line=order_line_obj.create(vals)
                obj.order_ids=[(4, order.id)]




