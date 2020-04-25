from odoo import fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ['sale.order']

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
