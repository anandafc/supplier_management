from odoo import models, fields, api, exceptions,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('supplier_management.rfp', string='Linked RFP', readonly=True)
    expected_delivery_date = fields.Date()
    terms_conditions = fields.Html(string='Terms & Conditions')
    warranty_period = fields.Integer(string='Warranty (Months)')
    score = fields.Integer()
    recommended = fields.Boolean()
    rfp_status = fields.Selection(related='rfp_id.status', store=True, string="RFP Status")
    # Fields for capturing unit price, quantity, and delivery charge
    order_line_ids = fields.One2many('purchase.order.line', 'order_id', string="Order Lines")
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    # @api.depends("order_line.price_total")
    # def _compute_total_price(self):
    #     """Computes the total price from order lines (product prices + delivery charges)."""
    #     for order in self:
    #         order.total_price = sum(order.order_line.mapped("price_total"))

    @api.depends('order_line_ids.price_subtotal', 'order_line_ids.delivery_charge')
    def _compute_total_amount(self):
        for order in self:
            total = sum(order.order_line_ids.mapped('price_subtotal')) + sum(
                order.order_line_ids.mapped('delivery_charge'))
            order.total_amount = total

    def action_accept(self):
        print('action accept')
        self.rfp_id.status = 'accepted'
        rfq = self.env['purchase.order'].search([('rfp_id', '=', self.id)])
        rfq.button_confirm()

    @api.constrains('recommended', 'partner_id', 'rfp_id')
    def _check_unique_recommended_per_supplier(self):
        for order in self:
            if order.recommended:
                existing_recommended = self.search([
                    ('rfp_id', '=', order.rfp_id.id),
                    ('partner_id', '=', order.partner_id.id),
                    ('recommended', '=', True),
                    ('id', '!=', order.id)  # Exclude the current record in case of updates
                ])
                if existing_recommended:
                    raise exceptions.ValidationError(_(
                        f"A company {order.partner_id.name} cannot have more than one recommended RFQ for the same RFP {order.rfp_id.name}."
                    ))
