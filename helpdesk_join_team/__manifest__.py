{
    'name': 'Helpdesk join team',
    'category': 'Website',
    'summary': 'Support join team',
    'license': 'AGPL-3',
    'version': '12.0.0.0',
    'description': """
Helpdesk join team
==================
Create an employee when accept a user to join the team.
    """,
    'depends': [
        'helpdesk_mgmt',
        'helpdesk_partner',
        'hr',
        'auth_signup',
    ],
    'data': [
        'data/helpdesk_join_team_data.xml',
        'view/helpdesk_ticket_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
