from odoo import fields, models


class HelpdeskAffectedSystem(models.Model):
    _name = 'helpdesk.ticket.affected_system'
    _description = 'Helpdesk Ticket Affected System'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('helpdesk.ticket')
    )
