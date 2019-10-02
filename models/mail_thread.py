# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import dateutil
import email
import hashlib
import hmac
import lxml
import logging
import pytz
import re
import socket
import time
import xmlrpclib

from collections import namedtuple
from email.message import Message
from email.utils import formataddr
from lxml import etree
from werkzeug import url_encode

from odoo import _, api, exceptions, fields, models, tools
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


#class MailThread(models.AbstractModel):
#    _inherit = 'mail.thread'

#    @api.multi
#    @api.returns('self', lambda value: value.id)
#    def message_post(self, body='', subject=None, message_type='notification',
#                     subtype=None, parent_id=False, attachments=None,
#                     content_subtype='html', **kwargs):
#        """ Post a new message in an existing thread, returning the new
#            mail.message ID.
#            :param int thread_id: thread ID to post into, or list with one ID;
#                if False/0, mail.message model will also be set as False
#            :param str body: body of the message, usually raw HTML that will
#                be sanitized
#            :param str type: see mail_message.type field
#            :param str content_subtype:: if plaintext: convert body into html
#            :param int parent_id: handle reply to a previous message by adding the
#                parent partners to the message in case of private discussion
#            :param tuple(str,str) attachments or list id: list of attachment tuples in the form
#                ``(name,content)``, where content is NOT base64 encoded
#            Extra keyword arguments will be used as default column values for the
#            new mail.message record. Special cases:
#                - attachment_ids: supposed not attached to any document; attach them
#                    to the related document. Should only be set by Chatter.
#            :return int: ID of newly created mail.message
#        """
#        if attachments is None:
#            attachments = {}
#        if self.ids and not self.ensure_one():
#            raise exceptions.Warning(_('Invalid record set: should be called as model (without records) or on single-record recordset'))

#        # if we're processing a message directly coming from the gateway, the destination model was
#        # set in the context.
#        model = False
#        if self.ids:
#            self.ensure_one()
#            model = self._context.get('thread_model', False) if self._name == 'mail.thread' else self._name
#            if model and model != self._name and hasattr(self.env[model], 'message_post'):
#                RecordModel = self.env[model].with_context(thread_model=None)  # TDE: was removing the key ?
#                return RecordModel.browse(self.ids).message_post(
#                    body=body, subject=subject, message_type=message_type,
#                    subtype=subtype, parent_id=parent_id, attachments=attachments,
#                    content_subtype=content_subtype, **kwargs)




#        email_cc = kwargs.get('email_cc')
#        print 'MailThread : email_cc=',email_cc



#        # 0: Find the message's author, because we need it for private discussion
#        author_id = kwargs.get('author_id')
#        if author_id is None:  # keep False values
#            author_id = self.env['mail.message']._get_default_author().id

#        # 1: Handle content subtype: if plaintext, converto into HTML
#        if content_subtype == 'plaintext':
#            body = tools.plaintext2html(body)

#        # 2: Private message: add recipients (recipients and author of parent message) - current author
#        #   + legacy-code management (! we manage only 4 and 6 commands)
#        partner_ids = set()
#        kwargs_partner_ids = kwargs.pop('partner_ids', [])
#        for partner_id in kwargs_partner_ids:
#            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
#                partner_ids.add(partner_id[1])
#            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
#                partner_ids |= set(partner_id[2])
#            elif isinstance(partner_id, (int, long)):
#                partner_ids.add(partner_id)
#            else:
#                pass  # we do not manage anything else
#        if parent_id and not model:
#            parent_message = self.env['mail.message'].browse(parent_id)
#            private_followers = set([partner.id for partner in parent_message.partner_ids])
#            if parent_message.author_id:
#                private_followers.add(parent_message.author_id.id)
#            private_followers -= set([author_id])
#            partner_ids |= private_followers

#        # 4: mail.message.subtype
#        subtype_id = kwargs.get('subtype_id', False)
#        if not subtype_id:
#            subtype = subtype or 'mt_note'
#            if '.' not in subtype:
#                subtype = 'mail.%s' % subtype
#            subtype_id = self.env['ir.model.data'].xmlid_to_res_id(subtype)

#        # automatically subscribe recipients if asked to
#        if self._context.get('mail_post_autofollow') and self.ids and partner_ids:
#            partner_to_subscribe = partner_ids
#            if self._context.get('mail_post_autofollow_partner_ids'):
#                partner_to_subscribe = filter(lambda item: item in self._context.get('mail_post_autofollow_partner_ids'), partner_ids)
#            self.message_subscribe(list(partner_to_subscribe), force=False)

#        # _mail_flat_thread: automatically set free messages to the first posted message
#        MailMessage = self.env['mail.message']
#        if self._mail_flat_thread and model and not parent_id and self.ids:
#            messages = MailMessage.search(['&', ('res_id', '=', self.ids[0]), ('model', '=', model), ('message_type', '=', 'email')], order="id ASC", limit=1)
#            if not messages:
#                messages = MailMessage.search(['&', ('res_id', '=', self.ids[0]), ('model', '=', model)], order="id ASC", limit=1)
#            parent_id = messages and messages[0].id or False
#        # we want to set a parent: force to set the parent_id to the oldest ancestor, to avoid having more than 1 level of thread
#        elif parent_id:
#            messages = MailMessage.sudo().search([('id', '=', parent_id), ('parent_id', '!=', False)], limit=1)
#            # avoid loops when finding ancestors
#            processed_list = []
#            if messages:
#                message = messages[0]
#                while (message.parent_id and message.parent_id.id not in processed_list):
#                    processed_list.append(message.parent_id.id)
#                    message = message.parent_id
#                parent_id = message.id

#        values = kwargs
#        values.update({
#            'author_id': author_id,
#            'model': model,
#            'res_id': model and self.ids[0] or False,
#            'body': body,
#            'subject': subject or False,
#            'message_type': message_type,
#            'parent_id': parent_id,
#            'subtype_id': subtype_id,
#            'partner_ids': [(4, pid) for pid in partner_ids],
#        })

#        # 3. Attachments
#        #   - HACK TDE FIXME: Chatter: attachments linked to the document (not done JS-side), load the message
#        attachment_ids = self._message_post_process_attachments(attachments, kwargs.pop('attachment_ids', []), values)
#        values['attachment_ids'] = attachment_ids

#        # Avoid warnings about non-existing fields
#        for x in ('from', 'to', 'cc'):
#            values.pop(x, None)



#        for key in values:
#            print 'message_post',key,values[key]



#        # Post the message
#        new_message = MailMessage.create(values)

#        print 'new_message=',new_message



#        # Post-process: subscribe author, update message_last_post
#        # Note: the message_last_post mechanism is no longer used.  This
#        # will be removed in a later version.
#        if (self._context.get('mail_save_message_last_post') and
#                model and model != 'mail.thread' and self.ids and subtype_id):
#            subtype_rec = self.env['mail.message.subtype'].sudo().browse(subtype_id)
#            if not subtype_rec.internal:
#                # done with SUPERUSER_ID, because on some models users can post only with read access, not necessarily write access
#                self.sudo().write({'message_last_post': fields.Datetime.now()})
#        if new_message.author_id and model and self.ids and message_type != 'notification' and not self._context.get('mail_create_nosubscribe'):
#            self.message_subscribe([new_message.author_id.id], force=False)
#        return new_message

