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


    is_description_entete = fields.Text('Description haut')
    is_description_pied1  = fields.Text('Description bas (Noir)')
    is_description_pied2  = fields.Text('Description bas (Bleu)')
    is_journal_banque_id  = fields.Many2one('account.journal', 'Journal de banque', domain=[('type','=','bank')])

    is_num_machine    = fields.Char('N° de machine')
    is_num_bl         = fields.Char('N° de BL')
    is_notre_ref      = fields.Char('Notre Réf N°')
    is_annee          = fields.Char('Année', compute='_compute', store=False, readonly=True)
    is_votre_commande = fields.Char('Votre commande')
    is_signature      = fields.Boolean('Signature direction', help="Ajouter la signature de la direction sur la facture")
