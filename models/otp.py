from odoo import models, fields, api
import random
import string
from datetime import timedelta

class SupplierOTPCode(models.Model):
    _name = 'supplier.otp'
    _description = 'Temporary OTP Storage for Supplier Verification'

    supplier_email = fields.Char(string="Supplier Email", required=True, index=True, unique=True)
    otp_code = fields.Char(string="OTP Code", required=True)
    valid_till = fields.Datetime(string="Expiration Time", required=True)
    is_otp_matched = fields.Boolean(string="OTP Confirmed", default=False)

    # _sql_constraints = [
    #     ('unique_supplier_email', 'unique(supplier_email)', 'An active OTP already exists for this email.')
    # ]

    @api.model
    def create_otp(self, supplier_email):
        """Generate a new OTP and replace any existing one for the given email."""
        existing_otp = self.search([('supplier_email', '=', supplier_email)])
        if existing_otp:
            existing_otp.unlink()

        new_otp = ''.join(random.choices(string.digits, k=6))
        expiry_time = fields.Datetime.now() + timedelta(minutes=5)

        otp_entry = self.create({
            'supplier_email': supplier_email,
            'otp_code': new_otp,
            'valid_till': expiry_time
        })

        return otp_entry

    def verify_otp(self, supplier_email, entered_otp):
        """Check if the provided OTP is valid and mark it as confirmed if correct."""
        otp_entry = self.search([
            ('supplier_email', '=', supplier_email),
            ('otp_code', '=', entered_otp),
            ('valid_till', '>', fields.Datetime.now())
        ], limit=1)

        max_attempts = 5
        attempts = self.search_count([('supplier_email', '=', supplier_email)])
        if attempts >= max_attempts:
            return False  # Too many attempts, reject OTP verification

        if otp_entry:
            otp_entry.write({'is_otp_matched': True})
            return True
        return False