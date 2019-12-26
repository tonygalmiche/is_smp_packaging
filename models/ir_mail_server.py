# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"


    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False):


#        print 'Cc=',message['Cc'],message['From']

#        cc=''
#        if message['From']:


#            cc=message['From']
#        message['Cc'] = cc

#Cc= tony.galmiche@gmail.com Administrator <tony.galmiche@free.fr>



#        print 'Cc=',message['Cc'],message['From']
#        print message

#        print '#### type=',type(message)

#        for line in message:
#            print 'line=',line




        res = super(IrMailServer, self).send_email(message, mail_server_id, smtp_server, smtp_port,
                   smtp_user, smtp_password, smtp_encryption, smtp_debug)

        return res


