{
    'name': 'Helpdesk Form',
    'category': 'Website',
    'sequence': 55,
    'summary': 'Generate ticket from a service form',
    'version': '2.0',
    'description': """
Generate ticket in the Helpdesk app from a form published.
    """,
    'depends': ['website_form', 'website_partner', 'helpdesk_mgmt'],
    'data': [
        'data/website_crm_data.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
