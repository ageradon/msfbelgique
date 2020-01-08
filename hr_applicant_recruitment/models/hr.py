# -*- coding: utf-8 -*-

# from openerp import api, fields, models
from odoo import api, fields, models #odoo13


class Employee(models.Model):
    _inherit = "hr.employee"
    
    applicant_education_ids = fields.One2many(
        'applicant.education',
        'employee_id',
        string='Educations'
    )
    applicant_employeement_ids = fields.One2many(
        'applicant.employeement',
        'employee_id',
        string='Employeements'
    )
    applicant_family_ids = fields.One2many(
        'applicant.family',
        'employee_id',
        string='Familys'
    )
    applicant_medical_ids = fields.One2many(
        'applicant.medical',
        'employee_id',
        string='Medical Checkup'
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: