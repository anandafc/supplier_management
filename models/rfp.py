from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SupplierRFP(models.Model):
    _name = "supplier.rfp"
    _description = "Request for Purchase"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"

    rfp_number = fields.Char(string="RFP Number", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
        ('recommendation', 'Recommendation'),
        ('accepted', 'Accepted'),
    ], string="Status", default='draft', tracking=True)

    required_date = fields.Date(string="Required Date", default=lambda self: fields.Date.add(fields.Date.today(), days=7))
    expiry_date = fields.Date(string="Expiry Date", required=True)
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id.id)

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, index=True)
    reviewer_id = fields.Many2one('res.users', string="Reviewer", default=lambda self: self.env.uid, readonly=True)
    approved_supplier_id = fields.Many2one('res.partner', string="Approved Supplier",
                                           domain="[('supplier_rank', '>', 0)]",
                                           help="Editable by approver only.")

    product_line_ids = fields.One2many('supplier.rfp.line', 'rfp_id', string="Product Lines")
    rfq_line_ids = fields.One2many('purchase.order', 'rfp_id', string="RFQ Lines")

    @api.model
    def create(self, vals):
        if vals.get('rfp_number', _('New')) == _('New'):
            vals['rfp_number'] = self.env['ir.sequence'].next_by_code('supplier.rfp.sequence') or _('New')
        return super(SupplierRFP, self).create(vals)

    @api.depends('rfq_line_ids', 'rfq_line_ids.amount_total', 'rfq_line_ids.state')
    def _compute_total_amount(self):
        """Computes total amount from accepted RFQ lines."""
        for rfp in self:
            total = sum(rfq.amount_total for rfq in rfp.rfq_line_ids.filtered(lambda rfq: rfq.state == 'accepted'))
            rfp.total_amount = total

    # ----- Reviewer Actions -----
    def action_submit(self):
        """Reviewer submits the RFP from Draft to Submitted."""
        if self.state != 'draft':
            raise UserError(_("Only a Draft RFP can be submitted."))
        self.state = 'submitted'

    def action_return_to_draft(self):
        """Reviewer returns a submitted RFP to Draft for further editing."""
        if self.state != 'submitted':
            raise UserError(_("Only a Submitted RFP can be returned to Draft."))
        self.state = 'draft'

    def action_recommend(self):
        """Reviewer recommends an RFP after closing it."""
        if self.state != 'closed':
            raise UserError(_("Only a Closed RFP can be recommended."))
        recommended_lines = self.rfq_line_ids.filtered(lambda l: l.recommended)
        if not recommended_lines:
            raise UserError(_("You must recommend at least one RFQ line."))
        self.state = 'recommendation'

    # ----- Approver Actions -----
    def action_approve(self):
        """Approver approves an RFP that is in Submitted state."""
        if self.state != 'submitted':
            raise UserError(_("Only a Submitted RFP can be approved."))
        self.state = 'approved'

    def action_reject(self):
        """Approver rejects an RFP that is in Submitted state."""
        if self.state != 'submitted':
            raise UserError(_("Only a Submitted RFP can be rejected."))
        self.state = 'rejected'

    def action_close(self):
        """Approver closes an Approved RFP, removing it from the portal."""
        if self.state != 'approved':
            raise UserError(_("Only an Approved RFP can be closed."))
        self.state = 'closed'

    def action_accept(self):
        """Approver creates a Purchase Order from an RFP in the Recommendation state."""
        if self.state != 'recommendation':
            raise UserError(_("Only an RFP in Recommendation state can be accepted."))
        if not self.approved_supplier_id:
            raise UserError(_("You must set an Approved Supplier first."))
        recommended_line = self.rfq_line_ids.filtered(lambda l: l.partner_id == self.approved_supplier_id and l.recommended)
        if not recommended_line:
            raise UserError(_("No recommended RFQ line found for the approved supplier."))

        po_vals = {
            'partner_id': self.approved_supplier_id.id,
            'origin': self.name,
        }
        self.env['purchase.order'].create(po_vals)
        self.state = 'accepted'


class SupplierRFPLine(models.Model):
    _name = "supplier.rfp.line"
    _description = "RFP Product Line"

    rfp_id = fields.Many2one('supplier.rfp', string="RFP", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", required=True)
    description = fields.Text(string="Description")
    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Monetary(string="Unit Price")
    delivery_charges_supplier = fields.Monetary(string="Delivery Charges")
    subtotal_price = fields.Monetary(string="Subtotal", compute="_compute_subtotal", store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id.id)

    @api.depends('quantity', 'unit_price', 'delivery_charges_supplier')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal_price = (line.quantity * line.unit_price) + line.delivery_charges_supplier


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    rfp_id = fields.Many2one('supplier.rfp', string="Related RFP")
    expected_delivery_date = fields.Date(string="Expected Delivery Date")
    terms_conditions = fields.Html(string="Terms and Conditions")
    warranty_period = fields.Integer(string="Warranty Period (months)")
    score = fields.Integer(string="Score")
    recommended = fields.Boolean(string="Recommended")
