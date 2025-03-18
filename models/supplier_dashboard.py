from odoo import models, fields, api
from datetime import datetime, timedelta
import json



class SupplierDashboard(models.TransientModel):
    _name = 'supplier_management.dashboard'
    _description = 'Supplier Management Dashboard'

    # Basic Fields
    supplier_id = fields.Many2one('res.partner', string='Supplier',
                                  domain=[('supplier_rank', '>', 0)])
    date_range = fields.Selection([
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('last_month', 'Last Month'),
        ('this_year', 'This Year'),
    ], string='Date Range', default='this_month')
    date_from = fields.Date(string='Start Date', required=False)
    date_to = fields.Date(string='End Date', required=False)

    # Computed Fields
    approved_rfq_count = fields.Integer(string='Approved RFQs', compute='_compute_dashboard_data')
    total_amount = fields.Float(string='Total Amount', compute='_compute_dashboard_data')
    product_breakdown = fields.Text(string='Product Breakdown', compute='_compute_dashboard_data')

    @api.depends('supplier_id', 'date_range', 'date_from', 'date_to')
    def _compute_dashboard_data(self):
        for record in self:
            # Calculate date range
            date_from, date_to = record._get_date_range()

            # Base domain for purchase orders
            domain = [('state', '=', 'purchase')]
            if record.supplier_id:
                domain.append(('partner_id', '=', record.supplier_id.id))
            if date_from:
                domain.append(('date_order', '>=', date_from))
            if date_to:
                domain.append(('date_order', '<=', date_to))

        # Compute metrics
        orders = self.env['purchase.order'].search(domain)
        record.approved_rfq_count = len(orders)
        record.total_amount = sum(orders.mapped('amount_total'))

        # Product breakdown
        product_data = {}
        # Search for purchase orders based on the current filters
        orders = self.env['purchase.order'].search([('state', '=', 'purchase')])
        for order in orders:
            for line in order.order_line:
                product = line.product_id
                product_name = product.name
                product_qty = line.product_qty
                if product_name in product_data:
                    product_data[product_name] += product_qty
                else:
                    product_data[product_name] = product_qty
        record.product_breakdown = json.dumps(product_data)

    def _get_date_range(self):
        """Calculate start and end dates based on selected range."""
        today = fields.Date.today()
        if self.date_range == 'today':
            return today, today
        elif self.date_range == 'this_week':
            monday = today - timedelta(days=today.weekday())
            return monday, today
        elif self.date_range == 'this_month':
            first_day = today.replace(day=1)
            return first_day, today
        elif self.date_range == 'last_month':
            last_month_end = today.replace(day=1) - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return last_month_start, last_month_end
        elif self.date_range == 'this_year':
            first_day = today.replace(month=1, day=1)
            return first_day, today
        return False, False