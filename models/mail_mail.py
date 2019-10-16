# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#import base64
#import datetime
#import logging
#import psycopg2
#import threading

#from email.utils import formataddr

#from odoo import _, api, fields, models
#from odoo import tools
#from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
#from odoo.tools.safe_eval import safe_eval

#_logger = logging.getLogger(__name__)


#class MailMail(models.Model):
#    _inherit = "mail.mail"


#    @api.model
#    def create(self, values):

#        print 'MailMail create = ',values
#        values['email_cc'] = 'tony.galmiche.ooo@free.fr'


#        # notification field: if not set, set if mail comes from an existing mail.message
#        if 'notification' not in values and values.get('mail_message_id'):
#            values['notification'] = True
#        if not values.get('mail_message_id'):
#            self = self.with_context(message_create_from_mail_mail=True)
#        new_mail = super(MailMail, self).create(values)
#        if values.get('attachment_ids'):
#            new_mail.attachment_ids.check(mode='read')
#        return new_mail





