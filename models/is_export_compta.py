# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
import unicodedata



class is_export_compta(models.Model):
    _name='is.export.compta'
    _order='name desc'

    name               = fields.Char(u"N°Folio"      , readonly=True)
    journal_id         = fields.Many2one('account.journal', u'Journal')
    date_debut         = fields.Date(u"Date de début", required=True)
    date_fin           = fields.Date(u"Date de fin"  , required=True)
    ligne_ids          = fields.One2many('is.export.compta.ligne', 'export_compta_id', u'Lignes')
    _defaults = {
    }


    @api.model
    def create(self, vals):
        data_obj = self.env['ir.model.data']
        sequence_ids = data_obj.search([('name','=','is_export_compta_seq')])
        if sequence_ids:
            sequence_id = data_obj.browse(sequence_ids[0].id).res_id
            vals['name'] = self.env['ir.sequence'].get_id(sequence_id, 'id')
        res = super(is_export_compta, self).create(vals)
        return res


    @api.multi
    def action_envoi_mail(self):
        body_html=u"""
        <html>
          <head>
            <meta content="text/html; charset=UTF-8" http-equiv="Content-Type">
          </head>
          <body>
            <font>Bonjour, </font>
            <br><br>
            <font>Ci-joint le fichier</font>
          </body>
        </html>
        """
        for obj in self:
            user  = self.env['res.users'].browse(self._uid)
            email = user.email
            nom   = user.name
            if email==False:
                raise Warning(u"Votre mail n'est pas renseigné !")
            if email:
                attachment_id = self.env['ir.attachment'].search([
                    ('res_model','=','is.export.compta'),
                    ('res_id'   ,'=',obj.id),
                    ('name'     ,'=','export-compta.txt')
                ])
                email_vals = {}
                email_vals.update({
                    'subject'       : 'Export compta Odoo',
                    'email_to'      : email, 
                    'email_from'    : email, 
                    'body_html'     : body_html.encode('utf-8'), 
                    'attachment_ids': [(6, 0, [attachment_id.id])] 
                })
                email_id=self.env['mail.mail'].create(email_vals)
                if email_id:
                    self.env['mail.mail'].send(email_id)


    @api.multi
    def action_export_compta(self):
        cr=self._cr
        for obj in self:
            obj.ligne_ids.unlink()
            sql="""
                SELECT  
                    aml.date,
                    aa.code, 
                    ai.number, 
                    rp.name, 
                    ai.type, 
                    'code_client',
                    ai.reference,
                    aj.name,
                    aml.name,
                    aml.debit, 
                    aml.credit,
                    aj.type
                FROM account_move_line aml left outer join account_invoice ai        on aml.move_id=ai.move_id
                                           inner join account_account aa             on aml.account_id=aa.id
                                           left outer join res_partner rp            on aml.partner_id=rp.id
                                           inner join account_journal aj             on aml.journal_id=aj.id
                WHERE aml.date>='"""+str(obj.date_debut)+"""' and aml.date<='"""+str(obj.date_fin)+"""' """
            if obj.journal_id:
                sql=sql+" and aml.journal_id="+str(obj.journal_id.id)

#            sql=sql+"""
#                GROUP BY aml.date, ai.number, rp.name, aa.code, ai.type, ai.date_due, rp.supplier,ai.reference,aj.name,aml.name
#                ORDER BY aml.date, ai.number, rp.name, aa.code, ai.type, ai.date_due, rp.supplier,ai.reference,aj.name,aml.name
#            """
            cr.execute(sql)

            for row in cr.fetchall():
                journal=str(row[7][-2:])
                compte=str(row[1])
                piece=str(row[2])
                if journal=='AC':
                    if row[6]:
                        piece=row[6]
                        #piece=str(row[6].encode('utf-8'))
                if piece=='None':
                    piece=''

                if row[11] in ['sale','purchase']:
                    libelle=(row[3] or u'')
                else:
                    libelle=(row[8] or u'')

                vals={
                    'export_compta_id'  : obj.id,
                    'date_facture'      : row[0],
                    'journal'           : journal,
                    'compte'            : compte,
                    'libelle'           : libelle,
                    'debit'             : row[9],
                    'credit'            : row[10],
                    'devise'            : u'E',
                    'piece'             : piece,
                    'commentaire'       : False,
                }

                #_logger.info(str(vals))


                self.env['is.export.compta.ligne'].create(vals)
            self.generer_fichier()


    def generer_fichier(self):
        for obj in self:
            model='is.export.compta'
            attachments = self.env['ir.attachment'].search([('res_model','=',model),('res_id','=',obj.id)])
            attachments.unlink()
            name='export-compta.txt'
            dest     = '/tmp/'+name
            f = open(dest,'wb')
            for row in obj.ligne_ids:

                compte=str(row.compte)
                if compte=='None':
                    compte=''
                debit=row.debit
                credit=row.debit
                if row.credit>0.0:
                    montant=row.credit  
                    sens='C'
                else:
                    montant=row.debit  
                    sens='D'
                montant=round(100*montant)
                montant=(u'000000000000'+'%0.0f' % montant)[-12:]
                date_facture=row.date_facture
                date_facture=datetime.datetime.strptime(date_facture, '%Y-%m-%d')
                date_facture=date_facture.strftime('%d%m%y')
                libelle=(row.libelle+u'                    ')[0:20]
                piece1=(row.piece[-5:]+u'        ')[0:5].encode('iso8859')
                piece2=(row.piece[-8:]+u'        ')[0:8].encode('iso8859')
                journal=row.journal
                f.write('M')
                f.write((compte+u'00000000')[0:8])
                f.write(journal)
                f.write('000')
                f.write(date_facture)
                f.write('F')

                libelle=unicodedata.normalize('NFKD', libelle).encode('ascii', 'ignore')

                try:
                    libelle=libelle.encode('iso8859')
                except ValueError:
                    raise Warning(u'Pb encodage '+libelle)



                f.write(libelle)
                f.write(sens)
                f.write('+')
                f.write(montant)
                f.write('        ')
                f.write('000000')
                f.write('     ')
                f.write(piece1)
                f.write('                    ')
                f.write(piece2)
                f.write('EUR'+journal+'    ')
                f.write(libelle)
                f.write('\r\n')

                #f.write(libelle.encode('utf-8'))
            f.close()
            r = open(dest,'rb').read().encode('base64')
            vals = {
                'name':        name,
                'datas_fname': name,
                'type':        'binary',
                'res_model':   model,
                'res_id':      obj.id,
                'datas':       r,
            }
            id = self.env['ir.attachment'].create(vals)


class is_export_compta_ligne(models.Model):
    _name = 'is.export.compta.ligne'
    _description = u"Lignes d'export en compta"
    _order='date_facture'

    export_compta_id = fields.Many2one('is.export.compta', u'Export Compta', required=True, ondelete='cascade')
    date_facture     = fields.Date(u"Date")
    journal          = fields.Char(u"Journal")
    compte           = fields.Char(u"N°Compte")
    piece            = fields.Char(u"Pièce")
    libelle          = fields.Char(u"Libellé")
    debit            = fields.Float(u"Débit")
    credit           = fields.Float(u"Crédit")
    devise           = fields.Char(u"Devise")
    commentaire      = fields.Char(u"Commentaire")

    _defaults = {
        'journal': 'VTE',
        'devise' : 'E',
    }







