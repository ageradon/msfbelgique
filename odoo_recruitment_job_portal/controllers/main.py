# -*- coding: utf-8 -*-

import base64
from odoo import http, _
from odoo.http import request
from odoo import models,registry, SUPERUSER_ID
# from odoo.addons.website_portal.controllers.main import website_account
# 
# class website_account(website_account):

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

class CustomerPortal(CustomerPortal):

#     @http.route()
#     def account(self, **kw):
#         """ Add applican documents to main account page """
#         response = super(CustomerPortal, self).account(**kw)
#         partner = request.env.user.partner_id
#         applicant = request.env['hr.applicant']
#         applicant_count = applicant.sudo().search_count([
#         ('applicant_user_id', '=', request.env.user.id)
#           ])
#         response.qcontext.update({
#         'applicant_count': applicant_count,
#         })
#         return response
        
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        applicant = request.env['hr.applicant']
        applicant_count = applicant.sudo().search_count([
        ('applicant_user_id', '=', request.env.user.id)
        ])
        values.update({
        'applicant_count': applicant_count,
        })
        return values
        
    @http.route(['/my/applicants', '/my/applicants/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_applicant(self, page=1, **kw):
        response = super(CustomerPortal, self)
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        applicant_obj = http.request.env['hr.applicant']
        domain = [
        ('applicant_user_id', '=', request.env.user.id)
        ]
        # count for pager
        applicant_count = applicant_obj.sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/applicants",
            total=applicant_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        applicants = applicant_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'applicants': applicants,
            'page_name': 'applicant',
            'pager': pager,
            'default_url': '/my/applicants',
        })
        return request.render("odoo_recruitment_job_portal.display_applicants", values)
        
    @http.route(['/my/applicant/<model("hr.applicant"):applicant>'], type='http', auth="user", website=True)
    def my_applicant(self, applicant=None, **kw):
        attachment_list = request.httprequest.files.getlist('attachment')
#         applicant_obj = applicant.sudo()
        applicant_obj = http.request.env['hr.applicant'].sudo().browse(applicant.id)
        for image in attachment_list:
            if kw.get('attachment'):
                attachments = {
                           'res_name': image.filename,
                           'res_model': 'hr.applicant',
                           'res_id': applicant_obj.id,
                           'datas': base64.encodestring(image.read()),
                           'type': 'binary',
                           'name': image.filename,
                       }
                attachment_obj = http.request.env['ir.attachment']
                attachment_obj.sudo().create(attachments)
        if len(attachment_list) > 0:
            group_msg = _('Applicant has sent %s attachments to application. Name of attachments are: ') % (len(attachment_list))
            for attach in attachment_list:
                group_msg = group_msg + '\n' + attach.filename
            group_msg = group_msg + '\n'  +  '. You can see top attachment menu to download attachments.'
            applicant_obj.sudo().message_post(body=group_msg,message_type='comment')
            customer_msg = _('%s') % (kw.get('applicant_comment'))
            applicant_obj.sudo().message_post(body=customer_msg,message_type='comment')
            return http.request.render('odoo_recruitment_job_portal.successful_applicant_send',{
            })
        if kw.get('applicant_comment'):
            customer_msg = _('%s') % (kw.get('applicant_comment'))
            applicant_obj.sudo().message_post(body=customer_msg,message_type='comment')
            return http.request.render('odoo_recruitment_job_portal.successful_applicant_send',{
            })
        return request.render("odoo_recruitment_job_portal.display_applicant", {'applicant': applicant_obj, 'user': request.env.user})
    
    
    @http.route(['/createapplication'], type='http', auth="user", website=True)
    def create_application(self, **post):
        jobs = request.env['hr.job'].sudo().search([('state','=','recruit')])
        job_values = {
                'job_id': jobs,
        }
        return http.request.render("odoo_recruitment_job_portal.create_application", job_values)
    

    @http.route(['/application'], type='http', auth="user", website=True)
    def submit_application(self, page=1, **kw):
        vals = {
                    'name' : 'Application For'+' '+kw['applicant_name'],
                    'partner_name': kw['applicant_name'],
                    'email_from': kw['email'],
                    'partner_phone': kw['phone'],
                    'job_id': int(kw['jobs']),
                    'applicant_user_id': request.env.user.id,
                    'description': kw['description'],
                }
        application = request.env['hr.applicant']
        application_obj = application.sudo().create(vals)
        attachment_list = request.httprequest.files.getlist('resume')
        for resume in attachment_list:
            attachments = {
                'res_name': resume.filename,
                'res_model': 'hr.applicant',
                'res_id': application_obj.id,
                'datas': base64.encodestring(resume.read()),
                'type': 'binary',
                'name': resume.filename,
            }
            attachment_obj = http.request.env['ir.attachment']
            attachment_obj.sudo().create(attachments)
        return request.render("odoo_recruitment_job_portal.successfull")
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
        
