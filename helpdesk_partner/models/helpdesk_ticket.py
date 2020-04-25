# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    partner_phone = fields.Char(string="Phone", track_visibility='onchange')
    partner_address = fields.Char(string="Address", track_visibility='onchange')
    partner_address_invoice = fields.Char(string="Invoice address",
                                          track_visibility='onchange')
    show_create_partner = fields.Boolean(compute="_compute_show_create_partner",
                                         readonly=True)

    @api.multi
    @api.depends('partner_id')
    def _compute_show_create_partner(self):
        for val in self:
            val.show_create_partner = not val.partner_id

    def create_res_partner(self, is_supplier=False, is_customer=False):
        if not self.partner_name:
            raise UserError(_('The partner name need to be filled.'))

        if not self.partner_email:
            raise UserError(_('The partner email need to be filled.'))

        values = {
            "name": self.partner_name,
            "supplier": is_supplier,
            "customer": is_customer,
            "street": self.partner_address,
            "email": self.partner_email,
            "phone": self.partner_phone,
        }

        partner_id = self.env['res.partner'].create(values)
        self.partner_id = partner_id.id
        return partner_id
