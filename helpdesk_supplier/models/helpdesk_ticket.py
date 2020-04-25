from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    show_create_supplier = fields.Boolean(compute="_compute_show_create_supplier",
                                          readonly=True)

    @api.multi
    @api.depends('category_id', 'partner_id')
    def _compute_show_create_supplier(self):
        data_category = self.env.ref(
            'helpdesk_supplier.helpdesk_ticket_category_supplier_applicant').id
        for val in self:
            if data_category == val.category_id.id:
                val.show_create_supplier = not val.partner_id or (
                            val.partner_id and not val.partner_id.supplier)

    def create_supplier(self):
        if not self.partner_id:
            self.create_res_partner(is_supplier=True)
        else:
            # Force set user is a supplier
            self.partner_id.supplier = True

    def send_supplier_applicant_mail(self):
        if self.partner_email:
            self.env.ref(
                'helpdesk_supplier.assignment_supplier_applicant_email_template'). \
                send_mail(self.id, email_values={}, force_send=True)

    @api.model_create_multi
    def create(self, vals_list):
        res_list = super(HelpdeskTicket, self).create(vals_list)

        for res in res_list:
            if res.category_id.id == self.env.ref(
                    'helpdesk_supplier.helpdesk_ticket_category_supplier_applicant').id:
                res.send_supplier_applicant_mail()

        return res
