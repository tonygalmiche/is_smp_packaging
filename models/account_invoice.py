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

    is_num_machine    = fields.Char(u'N° de machine')
    is_num_bl         = fields.Char(u'N° de BL')
    is_notre_ref      = fields.Char(u'Notre Réf N°')
    is_annee          = fields.Char(u'Année', compute='_compute', store=False, readonly=True)
    is_votre_commande = fields.Char(u'Votre commande')
    is_signature      = fields.Boolean(u'Signature direction', help=u"Ajouter la signature de la direction sur la facture")
    is_tampon         = fields.Boolean(u'Tampon direction'   , help=u"Ajouter le tampon avec la signature de la direction sur la facture")
