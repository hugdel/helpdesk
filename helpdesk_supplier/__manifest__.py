
{
    'name': 'Helpdesk supplier',
    'category': 'Website',
    'summary': 'Support supplier',
    'version': '12.0.0.0',
    'description': """

    """,
    'depends': [
        'helpdesk_partner'
    ],
    'data': [
        'view/helpdesk_ticket_view.xml',
        'data/helpdesk_supplier_data.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
