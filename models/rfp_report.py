from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import base64
import xlsxwriter
from datetime import datetime, time


class RFPReportWizard(models.TransientModel):
    _name = 'supplier_management.rfp.report.wizard'
    _description = 'RFP Report Wizard'

    supplier_id = fields.Many2one('res.partner', string="Supplier", required=True, domain=[('supplier_rank', '>', 0)])
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    company_logo = fields.Binary(string="Company Logo")
    excel_report = fields.Binary(string="Excel Report")  # Added field to store the report
    html_preview = fields.Html(string="HTML Preview", readonly=True)

    def _validate_inputs(self):
        """ Validates form inputs before generating the report """
        if self.start_date > self.end_date:
            raise UserError(_("Start date must be earlier than or equal to the end date."))

        # Adjusted to your model to fetch approved RFPs with supplier
        approved_rfps = self.env['supplier_management.rfp'].search([
            ('approved_supplier_id', '=', self.supplier_id.id),
            ('required_date', '>=', self.start_date),
            ('required_date', '<=', self.end_date),
            ('status', '=', 'accepted')
        ])

        if not approved_rfps:
            raise UserError(_("No accepted RFPs found for this supplier within the given date range."))

        if not self.supplier_id.image_1920:
            raise UserError(
                _("The selected supplier does not have a logo. Please upload a logo in the supplier profile."))

        return approved_rfps

    def action_generate_excel_report(self):
        if self.start_date > self.end_date:
            raise UserError(_('Start date must be earlier than or equal to End date.'))

        RFP = self.env['supplier_management.rfp']
        accepted_rfps = RFP.search([
            ('approved_supplier_id', '=', self.supplier_id.id),
            ('status', '=', 'accepted'),
            ('required_date', '>=', self.start_date),
            ('required_date', '<=', self.end_date)
        ])
        if not accepted_rfps:
            raise UserError(_('The selected supplier has no accepted RFPs.'))

        if not self.supplier_id.image_1920:
            raise UserError(_('The selected supplier does not have a logo.'))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('RFP Report')

        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)

        title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'left', 'font_color': '#4F81BD'})
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#4F81BD', 'font_color': '#FFFFFF', 'border': 1, 'align': 'center',
            'valign': 'vcenter'
        })
        date_format = workbook.add_format(
            {'num_format': 'dd/mm/yyyy', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        money_format = workbook.add_format(
            {'num_format': '#,##0.00', 'border': 1, 'align': 'right', 'valign': 'vcenter'})
        text_format = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
        total_format = workbook.add_format(
            {'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'right', 'valign': 'vcenter'})

        self.company_logo = self.supplier_id.image_1920
        logo_path = '/tmp/supplier_company_logo.png'
        with open(logo_path, 'wb') as f:
            f.write(base64.b64decode(self.company_logo))
        worksheet.insert_image('A1', logo_path, {'x_scale': 0.2, 'y_scale': 0.1})

        worksheet.merge_range('C1:E1', self.supplier_id.name, title_format)

        supplier_info = [
            ['Email', self.supplier_id.email or ''],
            ['Phone', self.supplier_id.phone or ''],
            ['Address', self.supplier_id.contact_address or ''],
            ['TIN', self.supplier_id.vat or ''],
            ['Bank Name', self.supplier_id.bank_ids and self.supplier_id.bank_ids[0].bank_id.name or ''],
            ['Account Name', self.supplier_id.bank_ids and self.supplier_id.bank_ids[0].acc_number or ''],
            ['Account Number', self.supplier_id.bank_ids and self.supplier_id.bank_ids[0].acc_number or ''],
            ['IBAN No.',
             self.supplier_id.bank_ids and self.supplier_id.bank_ids[0].bank_id and self.supplier_id.bank_ids[
                 0].bank_id.iban or ''],
            ['SWIFT Code',
             self.supplier_id.bank_ids and self.supplier_id.bank_ids[0].bank_id and self.supplier_id.bank_ids[
                 0].bank_id.bank_swift_code or ''],
        ]
        row = 2
        for label, value in supplier_info:
            worksheet.write(row, 2, label, header_format)
            worksheet.write(row, 3, value, text_format)
            row += 1

        row += 2
        worksheet.write(row, 0, 'RFP Number', header_format)
        worksheet.write(row, 1, 'Date', header_format)
        worksheet.write(row, 2, 'Required Date', header_format)
        worksheet.write(row, 3, 'Total Amount', header_format)
        row += 1

        net_total = 0.0
        for rfp in accepted_rfps:
            worksheet.write(row, 0, rfp.rfp_number, text_format)
            if rfp.create_date:
                rfp_date = fields.Datetime.from_string(rfp.create_date) if isinstance(rfp.create_date,
                                                                                      str) else rfp.create_date
                worksheet.write_datetime(row, 1, rfp_date, date_format)
            else:
                worksheet.write(row, 1, '', text_format)
            if rfp.required_date:
                req_date = datetime.combine(rfp.required_date, time.min)
                worksheet.write_datetime(row, 2, req_date, date_format)
            else:
                worksheet.write(row, 2, '', text_format)
            worksheet.write(row, 3, rfp.total_amount, money_format)
            net_total += rfp.total_amount
            row += 1

        worksheet.write(row, 2, 'Net Total', total_format)
        worksheet.write(row, 3, net_total, total_format)

        row += 2
        worksheet.write(row, 0, 'RFP ID', header_format)
        worksheet.write(row, 1, 'Product', header_format)
        worksheet.write(row, 2, 'Quantity', header_format)
        worksheet.write(row, 3, 'Unit Price', header_format)
        worksheet.write(row, 4, 'Delivery Charge', header_format)
        worksheet.write(row, 5, 'Subtotal', header_format)
        row += 1

        product_groups = {}
        for rfp in accepted_rfps:
            accepted_rfq = self.env['purchase.order'].search([
                ('rfp_id', '=', rfp.id),
                ('state', '=', 'purchase')
            ], limit=1)
            if accepted_rfq:
                for line in accepted_rfq.order_line_ids:
                    rfp_id = rfp.rfp_number
                    product = line.product_id.name
                    unit_price = line.price_unit
                    key = (rfp_id, product, unit_price)
                    if key not in product_groups:
                        product_groups[key] = {
                            'rfp_id': rfp_id,
                            'product': product,
                            'product_qty': 0,
                            'unit_price': unit_price,
                            'delivery_charge': 0,
                            'subtotal_price': 0,
                        }
                    product_groups[key]['product_qty'] += line.product_qty
                    product_groups[key]['delivery_charge'] += line.delivery_charge or 0
                    product_groups[key]['subtotal_price'] += line.price_subtotal

        rfp_sorted_data = {}
        for key, values in product_groups.items():
            rfp_id = key[0]
            if rfp_id not in rfp_sorted_data:
                rfp_sorted_data[rfp_id] = []
            rfp_sorted_data[rfp_id].append(values)

        total_product_total = 0.0
        for rfp_id, products in rfp_sorted_data.items():
            first_row = row
            for i, values in enumerate(products):
                if i == 0:
                    worksheet.write(first_row, 0, rfp_id, text_format)
                else:
                    worksheet.write_blank(row, 0, text_format)
                worksheet.write(row, 1, values['product'], text_format)
                worksheet.write(row, 2, values['product_qty'], text_format)
                worksheet.write(row, 3, values['unit_price'], money_format)
                worksheet.write(row, 4, values['delivery_charge'], money_format)
                worksheet.write(row, 5, values['subtotal_price'], money_format)
                total_product_total += values['subtotal_price']
                row += 1
            if len(products) > 1:
                worksheet.merge_range(first_row, 0, row - 1, 0, rfp_id, text_format)

        worksheet.write(row, 4, 'Total', total_format)
        worksheet.write(row, 5, total_product_total, total_format)

        # Add Company Contact Information at the end
        row += 2
        worksheet.write(row, 0, 'Company Contact Information', header_format)
        row += 1
        company_info = [
            ['Company Name', self.env.company.name or ''],
            ['Company Email', self.env.company.email or ''],
            ['Company Phone', self.env.company.phone or ''],
            ['Company Address', self.env.company.street or ''],
        ]
        for label, value in company_info:
            worksheet.write(row, 0, label, text_format)
            worksheet.write(row, 1, value, text_format)
            row += 1

        # Finalize and close the workbook
        workbook.close()
        output.seek(0)
        excel_data = base64.b64encode(output.read())
        self.excel_report = excel_data

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s/%s?download=true' % (self._name, self.id, 'excel_report'),
            'target': 'self',
        }

    def action_generate_html_preview(self):
        approved_rfps = self._validate_inputs()

        company = self.env.company
        supplier = self.supplier_id

        # Fetch supplier's logo using Odoo's web route
        logo_url = f"/web/image?model=res.partner&id={supplier.id}&field=image_1920" if supplier.image_1920 else ''

        # Supplier Info
        supplier_info = [
            ['Email', supplier.email or 'N/A'],
            ['Phone', supplier.phone or 'N/A'],
            ['Address', supplier.contact_address or 'N/A'],
            ['TIN', supplier.vat or 'N/A'],
            ['Bank Name', supplier.bank_ids and supplier.bank_ids[0].bank_id.name or 'N/A'],
            ['Account Name', supplier.bank_ids and supplier.bank_ids[0].acc_number or 'N/A'],
            ['Account Number', supplier.bank_ids and supplier.bank_ids[0].acc_number or 'N/A'],
            ['IBAN No.',
             supplier.bank_ids and supplier.bank_ids[0].bank_id and supplier.bank_ids[0].bank_id.iban or 'N/A'],
            ['SWIFT Code', supplier.bank_ids and supplier.bank_ids[0].bank_id and supplier.bank_ids[
                0].bank_id.bank_swift_code or 'N/A'],
        ]

        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="text-align: left;">
                         <img src="{logo_url}" alt="Supplier Company Logo" style="height: 60px;"/>
                    </td>
                    </td>
                    <td style="text-align: right; font-size: 18px; font-weight: bold;">
                        Request for Proposal Report Preview
                    </td>
                </tr>
            </table>
            <hr style="border: 1px solid #000;">

            <h3 style="background-color: #4F81BD; color: white; padding: 5px;">Supplier Information</h3>
            <div style="text-align: right;">
                <table border="1" cellpadding="5" cellspacing="0" width="50%" style="border-collapse: collapse; margin-left: auto;">
        """

        for label, value in supplier_info:
            html_content += f"""
                <tr>
                    <td style="font-weight: bold; width: 30%; text-align: center;">{label}</td>
                    <td style="text-align: center;">{value}</td>
                </tr>
            """

        html_content += """
                </table>
            </div>
            <br/>
        """

        # Approved RFPs Section
        html_content += """
            <h3 style="background-color: #4F81BD; color: white; padding: 5px;">Approved RFPs</h3>
            <table border="1" cellpadding="5" cellspacing="0" width="100%" style="border-collapse: collapse; text-align: center;">
                <tr style="background-color: #D9E1F2;">
                    <th>RFP Number</th>
                    <th>Date</th>
                    <th>Required Date</th>
                    <th style="text-align: right;">Total Amount</th>
                </tr>
        """

        net_total = 0.0
        for rfp in approved_rfps:
            rfp_date = rfp.create_date.strftime('%d-%m-%Y') if rfp.create_date else ''
            req_date = rfp.required_date.strftime('%d-%m-%Y') if rfp.required_date else ''
            total_amount = "{:,.2f}".format(rfp.total_amount)
            net_total += rfp.total_amount

            html_content += f"""
                <tr>
                    <td>{rfp.rfp_number}</td>
                    <td>{rfp_date}</td>
                    <td>{req_date}</td>
                    <td style="text-align: right;">{total_amount}</td>
                </tr>
            """

        html_content += f"""
            <tr style="background-color: #D9E1F2; font-weight: bold;">
                <td colspan="3" style="text-align: right;">Net Total</td>
                <td style="text-align: right;">{net_total:,.2f}</td>
            </tr>
            </table>
            <br/>
        """

        # Product Summary Section
        html_content += """
            <h3 style="background-color: #4F81BD; color: white; padding: 5px;">Product Summary</h3>
            <table border="1" cellpadding="5" cellspacing="0" width="100%" style="border-collapse: collapse; text-align: center;">
                <tr style="background-color: #D9E1F2;">
                    <th>RFP ID</th>
                    <th>Product</th>
                    <th style="text-align: right;">Quantity</th>
                    <th style="text-align: right;">Unit Price</th>
                    <th style="text-align: right;">Delivery Charge</th>
                    <th style="text-align: right;">Subtotal</th>
                </tr>
        """

        product_groups = {}
        for rfp in approved_rfps:
            accepted_rfq = self.env['purchase.order'].search([
                ('rfp_id', '=', rfp.id),
                ('state', '=', 'purchase')
            ], limit=1)

            if accepted_rfq:
                for line in accepted_rfq.order_line_ids:
                    key = (rfp.rfp_number, line.product_id.name, line.price_unit)

                    if key not in product_groups:
                        product_groups[key] = {
                            'rfp_id': rfp.rfp_number,
                            'product': line.product_id.name,
                            'product_qty': 0,
                            'unit_price': line.price_unit,
                            'delivery_charge': 0,
                            'subtotal_price': 0,
                        }
                    product_groups[key]['product_qty'] += line.product_qty
                    product_groups[key]['delivery_charge'] += line.delivery_charge or 0
                    product_groups[key]['subtotal_price'] += line.price_subtotal

        total_product_total = 0.0
        for values in product_groups.values():
            total_product_total += values['subtotal_price']
            html_content += f"""
                <tr>
                    <td>{values['rfp_id']}</td>
                    <td>{values['product']}</td>
                    <td style="text-align: right;">{values['product_qty']}</td>
                    <td style="text-align: right;">{values['unit_price']:,.2f}</td>
                    <td style="text-align: right;">{values['delivery_charge']:,.2f}</td>
                    <td style="text-align: right;">{values['subtotal_price']:,.2f}</td>
                </tr>
            """

        html_content += f"""
            <tr style="background-color: #D9E1F2; font-weight: bold;">
                <td colspan="5" style="text-align: right;">Total</td>
                <td style="text-align: right;">{total_product_total:,.2f}</td>
            </tr>
            </table>
            <br/>
        """

        # Fixed Company Contact Information Section with f-string
        html_content += f"""
                <h3 style="background-color: #4F81BD; color: white; padding: 5px;">Company Contact Information</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="font-weight: bold;">Company Email:</td><td>{company.email or 'N/A'}</td></tr>
                    <tr><td style="font-weight: bold;">Company Phone:</td><td>{company.phone or 'N/A'}</td></tr>
                    <tr><td style="font-weight: bold;">Company Address:</td><td>{company.street or 'N/A'}</td></tr>
                </table>
            </div>
            """
        print("Company Info:", company.name, company.email, company.phone, company.street)
        print("Current User Company:", self.env.user.company_id.name)
        self.html_preview = html_content

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',  # Keep it in the same wizard window
        }