
{
    'name': 'Helpdesk mailing list',
    'category': 'Website',
    'summary': 'Add partner to mailing list',
    'version': '12.0.0.0',
    'description': """

    """,
    'depends': ['mass_mailing', 'helpdesk_mgmt'],
    'data': [
        'wizard/helpdesk_create_mailing_list_views.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
