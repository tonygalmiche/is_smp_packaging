# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    @api.depends('date_invoice')
    def _compute(self):
        for obj in self:
            if obj.date_invoice:
                annee=datetime.strptime(obj.date_invoice, '%Y-%m-%d')
                annee=datetime.strftime(annee, '%y')
                obj.is_annee=annee


    is_description_entete = fields.Text(u'Description haut')
    is_description_pied1  = fields.Text(u'Description bas (Noir)')
    is_description_pied2  = fields.Text(u'Description bas (Bleu)')
    is_journal_banque_id  = fields.Many2one('account.journal', u'Journal de banque', domain=[('type','=','bank')])
    is_num_machine        = fields.Char(u'N° de machine')
    is_affaire_id         = fields.Many2one('is.affaire', u'Machine')
    is_num_bl             = fields.Char(u'N° de BL')
    is_notre_ref          = fields.Char(u'Notre Réf N°')
    is_annee              = fields.Char(u'Année', compute='_compute', store=False, readonly=True)
    is_votre_commande     = fields.Char(u'Votre commande')
    is_signature          = fields.Boolean(u'Signature direction', help=u"Ajouter la signature de la direction sur la facture")
    is_tampon             = fields.Boolean(u'Tampon direction'   , help=u"Ajouter le tampon avec la signature de la direction sur la facture")
    is_date_echeance      = fields.Date(u"Date d'échéance SMP")
    is_date_paiement      = fields.Date(u"Date paiement SMP", help="Champ spécifique pour SMP pour indiquer la date du paiement avant que la facture soit lettrée  1 mois plus tard")
    is_montant_en_lettres = fields.Char(u'Montant total en toutes lettres')


    @api.multi
    def write(self, vals):
        if not self.is_date_echeance and not vals.get('is_date_echeance'):
            vals['is_date_echeance']=self.date_due
        res=super(AccountInvoice, self).write(vals)
        return res


    def _prepare_invoice_line_from_po_line(self, line):
        data=super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        is_affaire_id=False
        if line.is_affaire_id:
            is_affaire_id=line.is_affaire_id.id
        data['is_affaire_id'] = is_affaire_id
        return data


    @api.multi
    def actualiser_affaire_sur_ligne_action(self):
        for obj in self:
            if obj.is_affaire_id:
                for line in obj.invoice_line_ids:
                    if not line.is_affaire_id:
                        line.is_affaire_id = obj.is_affaire_id


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    is_affaire_id = fields.Many2one('is.affaire', u'Machine')


    @api.onchange('product_id')
    def _onchange_product_id(self):
        res=super(AccountInvoiceLine, self)._onchange_product_id()
        is_affaire_id=False
        if self.purchase_line_id.order_id.is_affaire_id:
            is_affaire_id=self.purchase_line_id.order_id.is_affaire_id.id
        else:
            if self.invoice_id.is_affaire_id:
                is_affaire_id=self.invoice_id.is_affaire_id.id
        self.is_affaire_id=is_affaire_id
        return res


    # @api.onchange('sale_line_ids')
    # def _onchange_sale_line_ids(self):
    #     print self,self.sale_line_ids
    #     return True



