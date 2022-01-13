# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, tools, _
from odoo.osv import expression

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



class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            products = self.env['product.product']
            if operator in positive_operators:
                products = self.search([('default_code', '=', name)] + args, limit=limit)
                if not products:
                    products = self.search([('barcode', '=', name)] + args, limit=limit)
                if not products:
                    products = self.search([('is_ref_client', operator, name)] + args, limit=limit)
            if not products and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                products = self.search(args + [('default_code', operator, name)], limit=limit)
                if not limit or len(products) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(products)) if limit else False
                    products += self.search(args + [('name', operator, name), ('id', 'not in', products.ids)], limit=limit2)
            elif not products and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                products = self.search(domain, limit=limit)
            if not products and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    products = self.search([('default_code', '=', res.group(2))] + args, limit=limit)
            # still no results, partner in context: search on supplier info as last hope to find something
            if not products and self._context.get('partner_id'):
                suppliers = self.env['product.supplierinfo'].search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)])
                if suppliers:
                    products = self.search([('product_tmpl_id.seller_ids', 'in', suppliers.ids)], limit=limit)
        else:
            products = self.search(args, limit=limit)

        print(products)

        return products.name_get()




class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    is_certificat_matiere   = fields.Selection([('oui', 'Oui'),('non', 'Non')],u'Certificat matière')
    is_categorie_article_id = fields.Many2one('is.categorie.article', u'Catégorie')

