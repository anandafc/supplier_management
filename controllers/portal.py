from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
from odoo.http import request

class SupplierOTPPortal(CustomerPortal):
    @http.route(['/my/supplier2'], type='http', auth='public', website=True)
    def supplier_otp_page(self, **kw):
        """Render OTP verification page for supplier."""
        return request.render('supplier_management.supplier_otp_verification_template', {
            'page_name': 'supplier_otp',
        })

    @http.route(['/my/supplier2/request'], type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def generate_supplier_otp(self, **kwargs):
        """Generate and send OTP for supplier email verification."""
        supplier_email = kwargs.get('supplier_email')
        if not supplier_email:
            return request.render('supplier_management.supplier_otp_verification_template', {
                'error_message': 'Supplier email is required',
            })

        # Check if the email is already registered
        registered_user = request.env['res.users'].sudo().search([('login', '=', supplier_email)], limit=1)
        if registered_user:
            return request.render('supplier_management.supplier_otp_verification_template', {
                'error_message': 'This email is already associated with an existing account',
            })

        # Generate OTP
        otp_entry = request.env['supplier.otp'].sudo().create_otp(supplier_email)
        if not otp_entry:
            return request.render('supplier_management.supplier_otp_verification_template', {
                'error_message': 'Unable to generate OTP. Please try again.',
            })

        # Send OTP via email
        request.env['mail.mail'].sudo().create({
            'email_from': 'farhana.chowdhury@bjitacademy.com',
            'email_to': supplier_email,
            'subject': 'Supplier Verification Code',
            'body_html': f'<p>Your verification OTP is: <strong>{otp_entry.otp_code}</strong>. Please enter it within 5 minutes.</p>'
        }).send()
        return request.render('supplier_management.supplier_otp_verification_template', {
            'supplier_email': supplier_email,
            'display_otp_section': True,
        })

    @http.route(['/my/supplier2/validate'], type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def validate_supplier_otp(self, **kwargs):
        """Verify supplier's OTP entry."""
        supplier_email = kwargs.get('supplier_email')
        entered_otp = kwargs.get('entered_otp')

        if not supplier_email or not entered_otp:
            return request.render('supplier_management.supplier_otp_verification_template', {
                'error_message': 'Both email and OTP must be provided',
                'display_otp_section': True,
                'supplier_email': supplier_email,
            })

        # Validate OTP
        is_valid = request.env['supplier.otp'].sudo().verify_otp(supplier_email, entered_otp)
        if is_valid:
            return request.redirect('/my/supplier2/register?email=%s' % supplier_email)

        else:
            return request.render('supplier_management.supplier_otp_verification_template', {
                'error_message': 'Invalid or expired OTP. Please try again.',
                'display_otp_section': True,
                'supplier_email': supplier_email,
            })
