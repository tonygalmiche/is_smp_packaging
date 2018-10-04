# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class IsMatiere(models.Model):
    _name='is.matiere'
    _order='name'

    name = fields.Char("Matière", required=True)


class IsCategorieArticle(models.Model):
    _name='is.categorie.article'
    _order='name'

    name = fields.Char("Catégorie article", required=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_ref_client  = fields.Char("Référence client")
    is_matiere_id  = fields.Many2one('is.matiere', 'Matière')
    is_traitement  = fields.Char("Traitement")
    is_commentaire = fields.Text("Commentaire")


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    is_certificat_matiere   = fields.Selection([('oui', 'Oui'),('non', 'Non')],'Certificat matière')
    is_categorie_article_id = fields.Many2one('is.categorie.article', 'Catégorie')

