from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    problem_location = fields.Char(string="Problem location",
                                   track_visibility='onchange')
    affected_system_id = fields.Many2one('helpdesk.ticket.affected_system',
                                         string='Affected System',
                                         track_visibility='onchange')

    show_service_call = fields.Boolean(compute="_compute_show_service_call",
                                       readonly=True)

    severity = fields.Selection(selection=[
        ('0', _('Low')),
        ('1', _('Medium')),
        ('2', _('High')),
        ('3', _('Critical')),
    ], string='Severity', default='1', track_visibility='onchange')

    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        store=True,
        readonly=True,
        string='Company currency',
    )

    sale_amount_total = fields.Monetary(compute='_compute_sale_amount_total',
                                        string="Sum of Orders",
                                        help="Untaxed Total of Confirmed Orders",
                                        currency_field='company_currency_id')
    sale_number = fields.Integer(compute='_compute_sale_amount_total',
                                 string="Number of Quotations")
    order_number = fields.Integer(compute='_compute_sale_amount_total',
                                  string="Number of Orders")
    order_confirmed_number = fields.Integer(compute='_compute_sale_amount_total',
                                            string="Number of Orders confirmed")
    order_ids = fields.One2many('sale.order', 'ticket_id', string='Orders')

    @api.multi
    @api.depends('category_id')
    def _compute_show_service_call(self):
        data_category = self.env.ref(
            'helpdesk_service_call.helpdesk_ticket_category_service_call').id
        for val in self:
            val.show_service_call = data_category == val.category_id.id

    @api.depends('order_ids')
    def _compute_sale_amount_total(self):
        for ticket in self:
            total = 0.0
            nbr = 0
            nbr_order = 0
            company_currency = self.env.user.company_id.currency_id
            for order in ticket.order_ids:
                if order.state not in ('cancel',):
                    nbr_order += 1
                if order.state in ('draft', 'sent'):
                    nbr += 1
                if order.state not in ('draft', 'sent', 'cancel'):
                    total += order.currency_id._convert(
                        order.amount_untaxed, company_currency, order.company_id,
                        order.date_order or fields.Date.today())
            ticket.sale_amount_total = total
            ticket.sale_number = nbr
            ticket.order_number = nbr_order
            ticket.order_confirmed_number = ticket.order_number - ticket.sale_number

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        super(HelpdeskTicket, self)._onchange_partner_id()
        if self.partner_id:
            if self.partner_id.phone:
                self.partner_phone = self.partner_id.phone
            elif self.partner_id.mobile:
                self.partner_phone = self.partner_id.mobile

            if self.partner_id.street:
                self.partner_address = self.partner_id.street

            # Check invoice address
            lst_invoice_address = [i for i in self.partner_id.child_ids if
                                   i.type == "invoice"]
            if lst_invoice_address:
                self.partner_address_invoice = lst_invoice_address[0].street

    def generate_summary_ticket(self):
        severity_value = dict(
            self._fields["severity"]._description_selection(self.env)).get(
            self.severity)
        # TODO translate in english
        summary = """
        <b>Nom du client responsable :</b> {}<br />
        <b>Courriel du client responsable :</b> {}<br />
        <b>Téléphone du client responsable :</b> {}<br />
        <b>Adresse du client responsable :</b> {}<br />
        <br />
        <b>Sévérité de la situation :</b> {}<br />
        <b>Lieu du problème :</b> {}<br />
        <b>Système affecté :</b> {}<br />
        <b>Description du problème :</b> {}
        """.format(self.partner_name, self.partner_email, self.partner_phone,
                   self.partner_address,
                   severity_value, self.problem_location, self.affected_system_id.name,
                   self.description).strip()
        return summary

    def automated_handling(self):
        if not self.partner_id:
            raise UserError(_('The partner need to be filled.'))

        if not self.category_id or not (
                self.category_id.sale_order_template_id and self.category_id.sale_order_template_line_id):
            raise UserError(_('The category need a valid sale order template line.'))

        if not self.user_id:
            self.write({'user_id': self.env.user.id})

        values = {
            "ticket_id": self.id,
            "partner_id": self.partner_id.id,
            "sale_order_template_id": self.category_id.sale_order_template_id.id
        }
        # TODO mettre les adresses de partenaires

        order = self.env['sale.order'].create(values)
        if order.sale_order_template_id:
            # Force update sale order template
            order.onchange_sale_order_template_id()
        # Force confirm SO
        order.action_confirm()

        # TODO Link to project task
        # Write ticket information in created task
        tasks_ids = order.tasks_ids
        for task in tasks_ids:
            task.description = self.generate_summary_ticket()

    def send_user_service_call_mail(self):
        if self.partner_email:
            self.env.ref(
                'helpdesk_service_call.assignment_user_service_call_email_template'). \
                send_mail(self.id, email_values={}, force_send=True)

    @api.model_create_multi
    def create(self, vals_list):
        res_list = super(HelpdeskTicket, self).create(vals_list)

        for res in res_list:
            if res.category_id.id == self.env.ref(
                    'helpdesk_service_call.helpdesk_ticket_category_service_call').id:
                res.send_user_service_call_mail()

        return res
