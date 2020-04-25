
{
    'name': 'Helpdesk MRP',
    'category': 'Website',
    'summary': 'Support mrp in helpdesk',
    'version': '12.0.0.0',
    'description': """
Associate MRP
    """,
    'depends': [
        'helpdesk_supplier',
        'mrp_workcenters_machines',
    ],
    'data': [
        'view/helpdesk_ticket_view.xml',
        'view/mrp_workcenter_views.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
