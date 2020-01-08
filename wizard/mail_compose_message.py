# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def get_mail_values(self, res_ids):
        self.ensure_one()
        res = super(MailComposer, self).get_mail_values(res_ids)
        copie_ids=[]
        for key, value in res.iteritems():
            for partner in self.is_partner_copie_ids:
                copie_ids.append((4,partner.id))
            if 'author_id' in  value:
                copie_ids.append((4,value['author_id']))
            value['is_partner_copie_ids'] = copie_ids
        return res

    is_partner_copie_ids = fields.Many2many('res.partner','mail_compose_message_partner_copie_rel', 'mail_compose_id', 'partner_id', string='en Copie')


class Message(models.Model):
    _inherit = 'mail.message'

    is_partner_copie_ids = fields.Many2many('res.partner', 'mail_notification_partner_copie_rel', 'message_id', 'partner_id', string='en Copie')


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _notify_prepare_email_values(self, message):
        mail_values = super(Partner, self)._notify_prepare_email_values(message)
        cc_email_list = message.is_partner_copie_ids.mapped('email')

        #** Mettre en copie l'emetteur du mail *********************************
        #TODO : Ne fonctionne pas, car c'est l'admin par défaut
        #user  = self.env['res.users'].browse(self._uid)
        #email = user.email
        #if email:
        #    cc_email_list.append(email)
        #***********************************************************************

        partner_copie = {
            'email_cc': ",".join(cc_email_list),
        }
        mail_values.update(partner_copie)
        return mail_values

