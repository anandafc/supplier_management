# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.account.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo import http, _
from odoo.http import request, route
from odoo import fields
from collections import OrderedDict


class SupplierPortal(CustomerPortal):

    @http.route(["/my/supplier2/register"], type="http", methods=['POST', 'GET'], auth="public", website=True, csrf=True)
    def register_supplier(self, **kw):
        error_list = []
        success_list = []
        if request.httprequest.method == 'POST':
            vals = {}
            keys = [
                'company_name', 'email', 'phone', 'company_registered_address', 'company_alternate_address',
                'company_type_category', 'company_type', 'trade_license_number',
                'tax_identification_number', 'commencement_date', 'expiry_date',
                'contact_person_title', 'contact_email', 'contact_phone',
                'finance_contact_title', 'finance_contact_email', 'finance_contact_phone',
                'authorized_person_name', 'authorized_person_email', 'authorized_person_phone',
                'bank_name', 'bank_address', 'bank_swift_code', 'account_name',
                'account_number', 'iban', 'company_address_as_per_bank', 'client_1_name',
                'client_1_address', 'client_1_contact_email',
                'client_1_contact_phone', 'client_2_name',
                'client_2_contact_email', 'client_2_contact_phone', 'client_3_name',
                'client_3_address', 'client_3_contact_email',
                'client_3_contact_phone', 'certification', 'certificate_number',
                'certifying_body', 'award_date', 'certificate_expiry_date'
            ]
            for key in keys:
                if kw.get(key):
                    vals[key] = kw.get(key)
            if kw.get('tax_identification_number') and (len(kw.get('tax_identification_number')) != 15 or not kw.get(
                    'tax_identification_number').isdigit()):
                error_list.append("Tax Identification Number Should Be Of 15 Digits And All Digits")
            if kw.get('trade_license_number') and (len(kw.get('trade_license_number')) != 15 or not kw.get(
                    'trade_license_number').isdigit()):
                error_list.append("Trade License Number Should Be Of 15 Digits And All Digits")
            if kw.get('expiry_date') and fields.Date.to_date(kw.get('expiry_date')) <= fields.date.today():
                error_list.append("Expiry Date Should Be Greater Than Today")
            if not kw.get('company_name'):
                error_list.append("Company Name is mandatory")
            if not kw.get('email'):
                error_list.append("Company Email is mandatory")
            if kw.get('email'):
                already_exists = request.env['res.partner'].sudo().search([('email', '=', kw.get('email'))])
                if already_exists:
                    error_list.append("Company Email Already Exists In the system. Try with another email")
            file_fields = [
                'trade_license_business_registration', 'certificate_of_incorporation', 'certificate_of_good_standing',
                'establishment_card', 'vat_tax_certificate', 'memorandum_of_association',
                'identification_document_for_authorized_person', 'bank_letter_indicating_bank_account',
                'past_2_years_audited_financial_statements', 'other_certifications'
            ]

            file_vals = {}
            for field in file_fields:
                if kw.get(field):
                    file_vals[field] = kw.get(field).read()
            vals['state'] = 'submitted'

            if not error_list:
                new_supplier = request.env['supplier.registration'].sudo().create(vals)
                if new_supplier:
                    success_list.append("Supplier Registered Successfully")
                if file_vals:
                    new_supplier.write(file_vals)

        return request.render("supplier_management.new_supplier_registration_form_view_portal",
                              {'page_name': 'supplier_registration',
                               'error_list': error_list,
                               'success_list': success_list})


    @http.route(['/my/supplier', '/my/supplier/page/<int:page>'], type='http', auth='public', website=True)
    def get_supplier_list(self, page=1, sortby=None, search="", search_in='name', **kw):
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'expiry_date': {'label': _('Expiry Date'), 'order': 'expiry_date desc'},
        }
        domain = [('supplier_rank', '>=', 1)]
        search_list = {
            # 'all': {'label': _('All'), 'domain': []},
            'name': {'label': _('Name'), 'input': 'name', 'domain': [('name', 'ilike', search)]}
        }
        if not search_in:
            search_in = 'name'
        domain += search_list[search_in]['domain']
        total_supplier_count = request.env['res.partner'].sudo().search_count(domain)

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        page_detail = portal_pager(url='/my/supplier',
                                   total=total_supplier_count,
                                   url_args={'sortby': sortby, 'search_in': search_in, 'search': search},
                                   page=page,
                                   step=3)
        suppliers = request.env['res.partner'].sudo().search(domain, order=order,
                                                             limit=3, offset=page_detail['offset'])

        return request.render("supplier_management.supplier_list_view_portal", {'suppliers': suppliers,
                                                                          'page_name': 'supplier_list',
                                                                          'pager': page_detail,
                                                                          'searchbar_sortings': searchbar_sortings,
                                                                          'sortby': sortby,
                                                                          'search_in': search_in,
                                                                          'search': search,
                                                                          'searchbar_inputs': search_list,
                                                                          })

    @http.route(['/my/supplier/<int:supplier_id>'], type='http', auth='public', website=True)
    def get_supplier_details(self, supplier_id, **kw):
        supplier = request.env['res.partner'].sudo().browse(supplier_id)
        # pagination in detail view
        supplier_ids = request.env['res.partner'].sudo().search([('supplier_rank', '>=', 1)]).ids
        supplier_index = supplier_ids.index(supplier_id)
        supplier_count = len(supplier_ids)
        prev_supplier = supplier_ids[supplier_index - 1] if supplier_index > 0 else False
        next_supplier = supplier_ids[supplier_index + 1] if supplier_index < supplier_count - 1 else False
        return request.render("supplier_management.supplier_details_view_portal", {'supplier': supplier,
                                                                             'page_name': 'supplier_details',
                                                                             'prev_record': prev_supplier,
                                                                             'next_record': next_supplier})
