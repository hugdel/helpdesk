{
    'name': 'Helpdesk service call',
    'category': 'Website',
    'sequence': 55,
    'summary': 'Support service call',
    'version': '12.0.0.0',
    'description': """

    """,
    'depends': [
        'helpdesk_mgmt',
        'helpdesk_partner',
        'website_helpdesk',
        'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'view/sale_order_views.xml',
        'view/helpdesk_ticket_affected_system_view.xml',
        'view/helpdesk_ticket_category_view.xml',
        'view/helpdesk_ticket_view.xml',
        'view/helpdesk_ticket_templates.xml',
        'view/helpdesk_ticket_menu.xml',
        'data/helpdesk_service_call_data.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
