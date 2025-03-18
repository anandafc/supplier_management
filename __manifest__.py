{
    'name': 'Supplier Management',
    'version': '1.0',
    'summary': 'Manage supplier registration, RFP, and quotations',
    'description': 'A module to manage supplier registration, RFP creation, and quotation submission.',
    'author': 'Farhana Chowdhury Ananda',
    # 'website': 'https://yourwebsite.com',
    'category': 'Purchasing',
    'depends': ['base', 'web', 'portal', 'mail','purchase', 'contacts', 'account','website','sale','product',],  # Add 'mail' as a dependency
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',

        'views/portal_templates.xml',
        'views/supplier_registration_views.xml',
        'views/reviewer_views.xml',
        'views/res_partner_bank_inherit_views.xml',
        'views/bank_views_extended.xml',
        'views/res_partner_extended.xml',
        'views/email_templates.xml',
        'data/sequence.xml',
        'views/templates.xml',
        'views/rfp_views.xml',
        'views/rfp_portal_views.xml',
        'views/rfp_report.xml',
        # 'views/rfp_report_html_template.xml',

        # 'views/supplier_dashboard.xml',
        'views/dashboard_action.xml',
'views/menus.xml',


    ],
'assets': {
    'web.assets_backend': [
        'supplier_management/static/src/js/supplier_dashboard.js',
        'supplier_management/static/src/xml/supplier_dashboard.xml',
'supplier_management/static/src/css/dashboard.css',
'https://cdn.jsdelivr.net/npm/chart.js',
    ],
},

    'installable': True,
    'application': True,



}