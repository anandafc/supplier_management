# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class SupplierRegistration(models.TransientModel):
    _name = 'supplier.registration'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Supplier Registration'
    _rec_name = 'company_name'
    _order = 'create_date desc'

    company_name = fields.Char(string='Company Name')
    email = fields.Char(string='Company Email')
    phone = fields.Char(string='Company Phone')
    company_registered_address = fields.Char(string='Company Registered Address')
    company_alternate_address = fields.Char(string='Company Alternate Address')
    company_type_category = fields.Selection([
        ('LLC', 'LLC'),
        ('corporate', 'Corporation'),
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('partnership', 'Partnership'),
        ('cooperative', 'Cooperative')
    ], string='Company Category')
    trade_license_number = fields.Char(string='Trade License Number')
    tax_identification_number = fields.Char(string='Tax Identification Number')
    commencement_date = fields.Date(string='Commencement Date')
    expiry_date = fields.Date(string='Expiry Date')
    contact_person_title = fields.Char(string='Contact Person Title')
    contact_email = fields.Char(string='Contact Email')
    contact_phone = fields.Char(string='Contact Phone')
    finance_contact_title = fields.Char(string='Finance Contact Title')
    finance_contact_email = fields.Char(string='Finance Contact Email')
    finance_contact_phone = fields.Char(string='Finance Contact Phone')
    authorized_person_name = fields.Char(string='Authorized Person Name')
    authorized_person_email = fields.Char(string='Authorized Person Email')
    authorized_person_phone = fields.Char(string='Authorized Person Phone')
    bank_name = fields.Char(string='Bank Name')
    bank_address = fields.Char(string='Bank Address')
    bank_swift_code = fields.Char(string='Bank Swift Code')
    account_name = fields.Char(string='Account Name')
    account_number = fields.Char(string='Account Number')
    iban = fields.Char(string='IBAN')
    company_address_as_per_bank = fields.Char(string='Company Address as per Bank')
    client_1_name = fields.Char(string='Client 1 Name')
    client_1_address = fields.Char(string='Client 1 Address')
    client_1_contact_email = fields.Char(string='Client 1 Contact Email')
    client_1_contact_phone = fields.Char(string='Client 1 Contact Phone')
    client_2_name = fields.Char(string='Client 2 Name')
    client_2_address = fields.Char(string='Client 2 Address')
    client_2_contact_email = fields.Char(string='Client 2 Contact Email')
    client_2_contact_phone = fields.Char(string='Client 2 Contact Phone')
    client_3_name = fields.Char(string='Client 3 Name')
    client_3_address = fields.Char(string='Client 3 Address')
    client_3_contact_email = fields.Char(string='Client 3 Contact Email')
    client_3_contact_phone = fields.Char(string='Client 3 Contact Phone')
    certification = fields.Char(string='Certification')
    certificate_number = fields.Char(string='Certificate Number')
    certifying_body = fields.Char(string='Certifying Body')
    award_date = fields.Date(string='Award Date')
    certificate_expiry_date = fields.Date(string='Certificate Expiry Date')
    trade_license_business_registration = fields.Binary(string='Trade License/Business Registration')
    certificate_of_incorporation = fields.Binary(string='Certificate of Incorporation')
    certificate_of_good_standing = fields.Binary(string='Certificate of Good Standing')
    establishment_card = fields.Binary(string='Establishment Card')
    vat_tax_certificate = fields.Binary(string='VAT/TAX Certificate')
    memorandum_of_association = fields.Binary(string='Memorandum of Association')
    identification_document_for_authorized_person = fields.Binary(string='Identification Document for Authorized Person')
    bank_letter_indicating_bank_account = fields.Binary(string='Bank Letter indicating Bank Account')
    past_2_years_audited_financial_statements = fields.Binary(string='Past 2 Years Audited Financial Statements')
    other_certifications = fields.Binary(string='Other Certifications')
    # Declaration Field
    declaration = fields.Boolean(
        string="I confirm that all information and documents supplied are true and accurate to "
               "the best of my knowledge, and I understand that this information may be "
               "considered material in the evaluation of quotations, bids, and/or proposals.")
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('recommended', 'Recommended'),
            ('blacklisted', 'Blacklisted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            # ('submitted','Submit')
        ],
        string='Status',
        default='draft'
    )
    reviewer_notes = fields.Text(string='Reviewer Notes')


    def action_approve(self):

        vals = {
            'name': self.company_name or 'N/A',
            'email': self.email or 'N/A',
            'phone': self.phone or 'N/A',
            'company_registered_address': self.company_registered_address or 'N/A',
            'company_alternate_address': self.company_alternate_address or 'N/A',
            'company_type_category': self.company_type_category or 'N/A',
            'trade_license_number': self.trade_license_number or 'N/A',
            'tax_identification_number': self.tax_identification_number or 'N/A',
            'commencement_date': self.commencement_date or fields.Date.today(),
            'expiry_date': self.expiry_date or fields.Date.today(),
            'certification': self.certification or 'N/A',
            'certificate_number': self.certificate_number or 'N/A',
            'certifying_body': self.certifying_body or 'N/A',
            'award_date': self.award_date or 'N/A',
            'certificate_expiry_date': self.certificate_expiry_date or 'N/A',
            'supplier_rank': 1,
            'company_type': 'company',
        }
        vals = {k: v for k, v in vals.items() if v != 'N/A'}
        vals['child_ids'] = []
        vals['bank_ids'] = []
        if self.contact_person_title:
            vals['child_ids'].append((0, 0, {
                'name': self.contact_person_title,
                'email': self.contact_email,
                'phone': self.contact_phone,
                'type': 'contact',
            }))
        if self.authorized_person_name:
            vals['child_ids'].append((0, 0, {
                'name': self.authorized_person_name,
                'email': self.authorized_person_email,
                'phone': self.authorized_person_phone,
                'type': 'contact',
            }))
        if self.finance_contact_title:
            vals['child_ids'].append((0, 0, {
                'name': self.finance_contact_title,
                'email': self.finance_contact_email,
                'phone': self.finance_contact_phone,
                'type': 'contact',
            }))
        for client in range(1, 4):
            client_name = getattr(self, f'client_{client}_name', None)
            client_address = getattr(self, f'client_{client}_address', None)
            client_email = getattr(self, f'client_{client}_contact_email', None)
            client_phone = getattr(self, f'client_{client}_contact_phone', None)
            if client_name:
                vals['child_ids'].append((0, 0, {
                    'name': client_name,
                    'email': client_email,
                    'phone': client_phone,
                    'street': client_address,
                    'type': 'contact',
                }))

        if self.bank_name:
            bank_id = self.env['res.bank'].create({
                'name': self.bank_name,
                'street': self.bank_address,
                'bank_swift_code': self.bank_swift_code,
                'iban': self.iban,
            })
            vals['bank_ids'].append((0, 0, {
                'bank_id': bank_id.id,
                'acc_number': self.account_number,
                'acc_holder_name': self.account_name,
                'address': self.company_address_as_per_bank,
             }))
            # Check for file fields and add them to vals if present
        file_fields = [
            'trade_license_business_registration',
            'certificate_of_incorporation',
            'certificate_of_good_standing',
            'establishment_card',
            'vat_tax_certificate',
            'memorandum_of_association',
            'identification_document_for_authorized_person',
            'bank_letter_indicating_bank_account',
            'past_2_years_audited_financial_statements',
            'other_certifications'
        ]
        for field in file_fields:
            if getattr(self, field):
                vals[field] = getattr(self, field)
        new_supplier = self.env['res.partner'].create(vals)
        new_user = self.env['res.users'].create({
            'login': self.email,
            'password': self.email,
            'partner_id': new_supplier.id,
            'company_id': self.env.company.id,
            'groups_id': [(6, 0, self.env.ref('base.group_portal').ids)]
        })
        self.env.ref('supplier_management.supplier_registration_confirmation').send_mail(new_supplier.id)
        self.state = 'approved'
        # # Send Approval Email
        # template_id = self.env.ref('supplier_management.email_template_supplier_approval')
        # if template_id:
        #     template_id.sudo().send_mail(new_supplier.id, force_send=True)
        # else:
        #     raise UserError("Email template not found!")

        # Change State to Approved
        self.state = 'approved'


    def action_recommend_supplier(self):
        return {
            'name': 'Recommend Supplier',
            'type': 'ir.actions.act_window',
            'res_model': 'recommended.supplier',
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
            'context': {'default_supplier_id': self.id},
        }

    def action_blacklist_supplier(self):
        return {
            'name': 'Blacklist Supplier',
            'type': 'ir.actions.act_window',
            'res_model': 'blacklisted.supplier',
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
            'context': {'default_supplier_id': self.id},
        }

    def action_reject(self):
        self.state = 'rejected'

    # def action_submit(self):
    #     self.state = 'submitted'


class RecommendedSupplier(models.TransientModel):
    _name = 'recommended.supplier'
    _description = 'Recommended Supplier (Temporary)'

    supplier_id = fields.Many2one('supplier.registration', string='Supplier', required=True)
    reviewer_notes = fields.Text(string='Reviewer Notes')
    recommendation_date = fields.Date(string='Date', default=fields.Date.today())
    state = fields.Selection([
        ('recommended', 'Recommended'),
        ('blacklisted', 'Blacklisted'),
    ], string='State', default='recommended')

    def action_confirm_recommendation(self):
        # Update the main supplier model to mark as recommended
        supplier = self.supplier_id
        supplier.write({
            'reviewer_notes': self.reviewer_notes,  # Save reviewer notes
            'state': 'recommended',  # Update the state
        })

        return {'type': 'ir.actions.act_window_close'}

class BlacklistedSupplier(models.TransientModel):
    _name = 'blacklisted.supplier'
    _description = 'Blacklisted Supplier (Temporary)'

    supplier_id = fields.Many2one('supplier.registration', string='Supplier', required=True)
    reviewer_notes = fields.Text(string='Reviewer Notes')
    blacklist_date = fields.Date(string='Date', default=fields.Date.today())

    state = fields.Selection([
        ('recommended', 'Recommended'),
        ('blacklisted', 'Blacklisted'),
    ], string='State', default='blacklisted')

    def action_confirm_blacklist(self):
        # Update the main supplier model to mark as recommended
        supplier = self.supplier_id
        supplier.write({
            'reviewer_notes': self.reviewer_notes,  # Save reviewer notes
            'state': 'blacklisted',  # Update the state
        })


        return {'type': 'ir.actions.act_window_close'}