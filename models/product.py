# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class IsMatiere(models.Model):
    _name='is.matiere'
    _order='name'

    name = fields.Char(u"Matière", required=True)


class IsCategorieArticle(models.Model):
    _name='is.categorie.article'
    _order='name'

    name               = fields.Char(u"Catégorie article", required=True)
    account_income_id  = fields.Many2one('account.account', string=u"Compte de revenus")
    account_expense_id = fields.Many2one('account.account', string=u"Compte de dépenses")


    @api.multi
    def init_account_product_action(self):
        for obj in self:
            products = self.env['product.product'].search([('is_categorie_article_id','=',obj.id)])
            for product in products:
                print product
                product.property_account_expense_id = obj.account_expense_id
                product.property_account_income_id  = obj.account_income_id


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_ref_client           = fields.Char(u"Référence client")
    is_fabriquant           = fields.Char(u"Fabriquant")
    is_matiere_id           = fields.Many2one('is.matiere', u'Matière')
    is_traitement           = fields.Char(u"Traitement")
    is_commentaire          = fields.Text(u"Commentaire")
    is_certificat_matiere   = fields.Selection([('oui', 'Oui'),('non', 'Non')],u'Certificat matière')
    is_categorie_article_id = fields.Many2one('is.categorie.article', u'Catégorie')
    is_sh_code              = fields.Char(u"SH code")


    @api.onchange('is_categorie_article_id')
    def _is_categorie_article_id(self):
        if self.is_categorie_article_id:
            self.property_account_income_id  = self.is_categorie_article_id.account_income_id
            self.property_account_expense_id = self.is_categorie_article_id.account_expense_id


    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['property_account_income_id']  = self.property_account_income_id
        default['property_account_expense_id'] = self.property_account_expense_id
        return super(ProductTemplate, self).copy(default=default)


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    is_certificat_matiere   = fields.Selection([('oui', 'Oui'),('non', 'Non')],u'Certificat matière')
    is_categorie_article_id = fields.Many2one('is.categorie.article', u'Catégorie')

