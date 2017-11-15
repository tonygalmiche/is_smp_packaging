# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime
from openerp.exceptions import Warning


class is_export_compta(models.Model):
    _name='is.export.compta'
    _order='name desc'

    name               = fields.Char("N°Folio"      , readonly=True)
    journal_id         = fields.Many2one('account.journal', 'Journal')
    date_debut         = fields.Date("Date de début", required=True)
    date_fin           = fields.Date("Date de fin"  , required=True)
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
                    sum(aml.debit), 
                    sum(aml.credit)
                FROM account_move_line aml left outer join account_invoice ai        on aml.move_id=ai.move_id
                                           inner join account_account aa             on aml.account_id=aa.id
                                           inner join res_partner rp                 on aml.partner_id=rp.id
                                           inner join account_journal aj             on aml.journal_id=aj.id
                WHERE aml.date>='"""+str(obj.date_debut)+"""' and aml.date<='"""+str(obj.date_fin)+"""' """


            if obj.journal_id:
                sql=sql+" and aml.journal_id="+str(obj.journal_id.id)

            sql=sql+"""
                GROUP BY aml.date, ai.number, rp.name, aa.code, ai.type, ai.date_due, rp.supplier,ai.reference,aj.name
                ORDER BY aml.date, ai.number, rp.name, aa.code, ai.type, ai.date_due, rp.supplier,ai.reference,aj.name
            """
            cr.execute(sql)
            for row in cr.fetchall():
                journal=str(row[7][-2:])
                compte=str(row[1])
                #if obj.type_interface=='ventes' and compte=='411100':
                #    compte=str(row[5])
                piece=str(row[2])
                if journal=='AC':
                    piece=str(row[6])
                if piece=='None':
                    piece=''
                vals={
                    'export_compta_id'  : obj.id,
                    'date_facture'      : row[0],
                    'journal'           : journal,
                    'compte'            : compte,
                    'libelle'           : row[3],
                    'debit'             : row[8],
                    'credit'            : row[9],
                    'devise'            : u'E',
                    'piece'             : piece,
                    'commentaire'       : False,
                }
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
                piece1=(row.piece[-5:]+u'        ')[0:5]
                piece2=(row.piece[-8:]+u'        ')[0:8]
                journal=row.journal
                f.write('M')
                f.write((compte+u'00000000')[0:8])
                f.write(journal)
                f.write('000')
                f.write(date_facture)
                f.write('F')
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

    export_compta_id = fields.Many2one('is.export.compta', 'Export Compta', required=True, ondelete='cascade')
    date_facture     = fields.Date("Date")
    journal          = fields.Char("Journal")
    compte           = fields.Char("N°Compte")
    piece            = fields.Char("Pièce")
    libelle          = fields.Char("Libellé")
    debit            = fields.Float("Débit")
    credit           = fields.Float("Crédit")
    devise           = fields.Char("Devise")
    commentaire      = fields.Char("Commentaire")

    _defaults = {
        'journal': 'VTE',
        'devise' : 'E',
    }







