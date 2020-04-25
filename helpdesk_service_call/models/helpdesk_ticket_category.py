from odoo import api, fields, models


class HelpdeskCategory(models.Model):
    _inherit = 'helpdesk.ticket.category'

    sale_order_template_id = fields.Many2one('sale.order.template', default_model='sale.order',
                                             string='Template Sale Order',
                                             help='Enables the usage of the template when the ticket is handled for '
                                                  'the quote creation.')

    sale_order_template_line_id = fields.Many2one(
        'sale.order.template.line', default_model='sale.order.line', string='Service task',
        domain="[('sale_order_template_id', '=', sale_order_template_id), "
               "('product_id.type', '=', 'service'), "
               "('product_id.service_tracking', 'in', ('task_new_project', 'project_only'))]",
        help='Sale order template line to be filled by the ticket\'s description.')

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        self.sale_order_template_line_id = None
