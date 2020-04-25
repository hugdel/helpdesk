{
    'name': 'Helpdesk partner',
    'category': 'Website',
    'summary': 'Support more information about partner',
    'license': 'AGPL-3',
    'version': '12.0.0.0',
    'description': """
Helpdesk partner
================
Support more fields of partner and add button to create res.partner.
    """,
    'depends': [
        'helpdesk_mgmt',
    ],
    'data': [
        'view/helpdesk_ticket_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
