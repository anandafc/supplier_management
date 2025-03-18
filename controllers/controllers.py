from odoo.addons.portal.controllers.portal import CustomerPortal,pager as portal_pager
from odoo.http import request
from odoo import http, _
from operator import itemgetter


class PortalRFPController(http.Controller):

    @http.route(['/my/rfps', '/my/rfps/page/<int:page>'], type='http', auth='public', website=True)
    def portal_my_rfps(self, page=1, sortby=None, search=None, search_in='all', **kw):
        # Add sort by feature
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'total_amount': {'label': _('Total Amount'), 'order': 'total_amount'},
        }

        # Default search_in is 'all', if no search_in parameter provided
        if not search_in:
            search_in = 'all'

        # Search options
        search_list = {
            'all': {'label': _('All'), 'input': 'all', 'domain': []},
            'product': {'label': _('Product'), 'input': 'product', 'domain': [('product_line_ids.product_id.name', 'ilike', search)]},
            'status': {'label': _('Status'), 'input': 'status', 'domain': [('status', '=', search)]},
        }

        # Set search domain based on selected search_in option
        search_domain = search_list[search_in]['domain']
        print("Search Domain:", search_domain)  # Debugging line

        # Default sorting is by 'date' if no sortby parameter is provided
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Get the total count of RFPs for pagination
        rfp_count = request.env['supplier_management.rfp'].search_count([])
        pager = request.website.pager(
            url='/my/rfps',
            total=rfp_count,
            page=page, step=5,
            scope=5,
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search}
        )

        # Get the list of RFPs based on domain and order (no grouping)
        rfps = request.env['supplier_management.rfp'].search(search_domain, limit=5, offset=pager['offset'], order=order)
        print(rfps)
        for rfp in rfps:
            print("RFP Product Lines:", rfp.product_line_ids)  # Debugging line

        # Pass the RFPs and other context to the template
        return request.render('supplier_management.portal_my_rfps', {
            'rfps': rfps,  # No grouping, just pass the list of RFPs
            'page_name': 'my_rfps',
            'pager': pager,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': search_list,
            'search_in': search_in,
            'search': search,
            'default_url': '/my/rfps',
        })

    @http.route('/my/rfp/<int:rfp_id>', auth='public', website=True)
    def portal_rfp_details(self, rfp_id, **kw):
        """ Displays full details of a selected RFP. """
        rfp = request.env['supplier_management.rfp'].sudo().browse(rfp_id)

        # Check if RFP exists
        if not rfp:
            return request.redirect('/my/rfps')

        return request.render('supplier_management.rfp_form_view_template', {'rfp': rfp})

    @http.route(['/my/rfp/<int:rfp_id>/submit_rfq'], type='http', auth='public', website=True)
    def portal_submit_rfq(self, rfp_id, **kw):
        """ Handles RFQ submission for an RFP. Allows multiple RFQs per vendor and ensures proper Buyer & Vendor names. """

        rfp = request.env['supplier_management.rfp'].sudo().browse(rfp_id)

        # Check if RFP exists
        if not rfp:
            return request.redirect('/my/rfps')

        # Ensure the Partner ID is properly linked (Vendor)
        partner = request.env.user.partner_id
        if not partner:
            return request.redirect('/my/rfps')

        # Assign Buyer (supplier - The one who created the RFP)
        buyer = rfp.create_uid  # The user who created the RFP

        # Allow Multiple RFQs from the Same Vendor
        rfq_values = {
            'rfp_id': rfp.id,
            'partner_id': partner.id,  # Vendor (Supplier submitting RFQ)
            'user_id': buyer.id,  # Buyer (Procurement User who created the RFP)
            'expected_delivery_date': kw.get('expected_delivery_date'),
            'terms_conditions': kw.get('terms_conditions'),
            'warranty_period': kw.get('warranty_period'),
            'state': 'draft',  # Ensure RFQ is created in Draft state
        }

        # Create RFQ (Purchase Order)
        rfq = request.env['purchase.order'].sudo().create(rfq_values)

        # Add RFQ Lines
        for line in rfp.product_line_ids:
            rfq_line_values = {
                'order_id': rfq.id,
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'price_unit': float(kw.get(f'price_unit_{line.id}', 0.0)),
                'delivery_charge': float(kw.get(f'delivery_charge_{line.id}', 0.0)),
            }
            request.env['purchase.order.line'].sudo().create(rfq_line_values)

        # Redirect back to the RFP details page
        return request.redirect(f'/my/rfp/{rfp.id}')


class RFQPortalController(http.Controller):
    @http.route('/my/rfqs', type='http', auth='user', website=True)
    def portal_my_rfqs(self, **kw):
        # Get the current user's RFQs (purchase orders) related to RFP
        rfqs = request.env['purchase.order'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id),  # Only fetch RFQs created by the current user
            ('rfp_id', '!=', False)  # Ensure the RFQ is linked to an RFP
        ])

        return request.render('supplier_management.portal_my_rfqs', {
            'rfqs': rfqs,
        })
