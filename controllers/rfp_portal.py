from odoo import http
from odoo.http import request

class PortalRFP(http.Controller):
    @http.route(['/my/rfps', '/my/rfps/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_rfps(self, **kw):
        rfps = request.env['rfp.request'].search([('reviewer_id', '=', request.env.user.id)])
        return request.render('supplier_management.portal_my_rfps_list', {'rfps': rfps})

    @http.route('/my/rfps/<int:rfp_id>', type='http', auth="user", website=True)
    def portal_rfp_form(self, rfp_id, **kw):
        rfp = request.env['rfp.request'].browse(rfp_id)
        return request.render('supplier_management.portal_rfp_form_view', {'rfp': rfp})