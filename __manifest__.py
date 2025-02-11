{
    'name': 'Supplier Management',
    'version': '1.0',
    'summary': 'Manage supplier registration, RFP, and quotations',
    'description': 'A module to manage supplier registration, RFP creation, and quotation submission.',
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'category': 'Purchasing',
    'depends': ['base', 'web', 'portal', 'mail','purchase', 'contacts', 'account','website','sale'],  # Add 'mail' as a dependency
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        # 'views/supplier_views.xml',
        'views/portal_templates.xml',
        'views/supplier_registration_views.xml',
        'views/reviewer_views.xml',
        'views/res_partner_bank_inherit_views.xml',
        'views/bank_views_extended.xml',
        'views/res_partner_extended.xml',
        'views/email_templates.xml',
        # 'views/final_updated_templates.xml'
        'views/templates.xml',
        'data/sequence.xml',
'views/menus.xml',
        'views/rfp_views.xml',


    ],
    'installable': True,
    'application': True,
}