from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import ValidationError
# import logging
# _logger = logging.getLogger(__name__)

class RFP(models.Model):
    _name = "supplier_management.rfp"
    _description = "Request for Purchase"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _log_access = True
    _rec_name = "rfp_number"

    rfp_number = fields.Char(string="RFP Number", required=True, copy=False, readonly=True, default='New',store=True)


    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
        ('recommendation', 'Recommendation'),
        ('accepted', 'Accepted'),
    ], string="Status", default="draft", tracking=True)

    required_date = fields.Date(string="Required Date", default=lambda self: fields.Date.today() + timedelta(days=7), tracking=True)

    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    total_amount = fields.Monetary(string="Total Amount", currency_field="currency_id", compute="_compute_total_amount", store=True)

    reviewer_id = fields.Many2one('res.users', string="Reviewer", required=True, default=lambda self: self.env.user, tracking=True)
    approver_id = fields.Many2one('res.users', string="Approver", tracking=True)

    approved_supplier_id = fields.Many2one('res.partner', string="Approved Supplier", domain="[('id', 'in', recommended_supplier_ids)]", tracking=True)
    recommended_supplier_ids = fields.Many2many('res.partner', string="Recommended Suppliers", compute="_compute_recommended_suppliers")

    product_line_ids = fields.One2many("supplier_management.rfp.product", "rfp_id", string="Product Lines")

    rfq_line_ids = fields.One2many("purchase.order", "rfp_id", string="RFQ Lines")

    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, readonly=True)

    @api.depends('rfq_line_ids.order_line.price_subtotal')
    def _compute_total_amount(self):
        for rfp in self:
            total = sum(rfp.rfq_line_ids.mapped('order_line.price_subtotal'))
            rfp.total_amount = total

    def _compute_recommended_suppliers(self):
        for rfp in self:
            recommended_rfq_lines = rfp.rfq_line_ids.filtered(lambda r: r.recommended)
            rfp.recommended_supplier_ids = recommended_rfq_lines.mapped('partner_id')

    @api.model
    def create(self, vals):
        # Generate the RFP number using the sequence if it's not set already
        if vals.get('rfp_number', _('New')) == _('New'):
            # Using the ir.sequence model to get the next RFP number
            vals['rfp_number'] = self.env['ir.sequence'].next_by_code('supplier_management.rfp') or _('New')

        return super(RFP, self).create(vals)

    def action_submit(self):
        self.write({'status': 'submitted'})
        approver_group = self.env.ref('supplier_management.group_supplier_management_approver')
        for approver in approver_group.users:
            self.message_post(
                body=_("RFP <b>%s</b> has been submitted and is pending approval.") % self.rfp_number,
                partner_ids=[approver.partner_id.id]
            )

    def action_recommend(self):
        recommended_rfq = self.env['purchase.order'].search([('rfp_id', '=', self.id), ('recommended', '=', True)])

        if not recommended_rfq:
            raise ValidationError(_("You must have at least one recommended RFQ before proceeding."))

        self.write({'status': 'recommendation'})
        approver_group = self.env.ref('supplier_management.group_supplier_management_approver')
        for approver in approver_group.users:
            self.message_post(
                body=_("RFP <b>%s</b> has been recommended and is pending final approval.") % self.rfp_number,
                partner_ids=[approver.partner_id.id]
            )

    def action_return_draft(self):
        if self.status != 'submitted':
            raise ValidationError(_("You can only return an RFP to Draft when it's in the Submitted state."))
        self.write({'status': 'draft'})
        self.message_post(
            body=_("RFP <b>%s</b> has been returned to Draft for modifications.") % self.rfp_number,
            partner_ids=[self.create_uid.partner_id.id]  # Notify the creator
        )

    def action_approve(self):
        """ Approves the RFP, Notifies the Reviewer & Suppliers """
        self.write({'status': 'approved'})

        # Notify the Reviewer about the approval
        if self.reviewer_id:
            self.message_post(
                body=_("RFP <b>%s</b> has been Approved.") % self.rfp_number,
                partner_ids=[self.reviewer_id.partner_id.id]
            )

        # Notify Suppliers about the new RFP for quotations
        supplier_group = self.env.ref("base.group_portal")
        for supplier in supplier_group.users:
            self.message_post(
                body=_("A new RFP <b>%s</b> is now open for quotations.") % self.rfp_number,
                partner_ids=[supplier.partner_id.id]
            )

    def action_reject(self):
        """ Rejects the RFP and notifies the Reviewer """
        self.write({'status': 'rejected'})

        # Notify the Reviewer about the rejection
        if self.reviewer_id:
            self.message_post(
                body=_("RFP <b>%s</b> has been Rejected.") % self.rfp_number,
                partner_ids=[self.reviewer_id.partner_id.id]
            )

    def action_close(self):
        """ Closes the RFP and removes it from the portal """
        self.write({'status': 'closed'})
        self.message_post(body=_("RFP <b>%s</b> has been Closed.") % self.rfp_number)

    def action_accept(self):
        """ Accepts the recommended RFQ and converts it into a PO """
        # Search for the recommended RFQ
        recommended_rfq = self.env['purchase.order'].search([('rfp_id', '=', self.id), ('recommended', '=', True)],
                                                            limit=1)

        if not recommended_rfq:
            raise ValidationError(_("There must be a recommended RFQ before accepting the RFP."))

        # Set the status to 'accepted'
        self.write({'status': 'accepted'})

        # Set the approved supplier ID based on the recommended RFQ
        self.approved_supplier_id = recommended_rfq.partner_id  # Set the approved supplier from the recommended RFQ

        # Create Purchase Order (PO) from the recommended RFQ
        po_values = {
            'partner_id': recommended_rfq.partner_id.id,  # Supplier (Vendor) who submitted the RFQ
            'rfp_id': self.id,  # Link the PO to the current RFP
            'date_order': fields.Date.today(),  # Set today's date as the order date
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,  # Product from the RFQ line
                'product_qty': line.product_qty,  # Quantity of the product
                'price_unit': line.price_unit,  # Unit price from the RFQ line
                'delivery_charge': line.delivery_charge,  # Delivery charge from the RFQ line
            }) for line in recommended_rfq.order_line],  # Create PO lines from the RFQ order lines
        }

        # Create the Purchase Order
        po = self.env['purchase.order'].create(po_values)

        # Post a message to the RFP, notifying that the PO has been created
        self.message_post(body=_("RFP <b>%s</b> has been accepted and a Purchase Order <b>%s</b> has been created.") % (
        self.rfp_number, po.name))
