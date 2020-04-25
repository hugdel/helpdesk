# Copyright 2020 TechnoLibre <info@technolibre.ca>
# License AGPLv3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

import logging
from odoo import _, fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HelpdeskMergeCategoryWizard(models.TransientModel):
    _name = 'helpdesk.merge.category.wizard'

    @api.model
    def default_get(self, fields):
        result = super(HelpdeskMergeCategoryWizard, self).default_get(fields)
        category_ids = self.env.context.get('active_ids', [])

        # Force remove list of category specified from modules
        # Can be add after, just prevent error from user
        # category from module cannot be deleted
        undeleted_categories = [a.res_id for a in
                                self.env["ir.model.data"].sudo().search(
                                    [('model', '=', 'helpdesk.ticket.category')])]
        unlink_category_ids = list(set(category_ids).difference(
            set(undeleted_categories)))
        result["helpdesk_categories_to_merge"] = [(6, 0, unlink_category_ids)]
        return result

    helpdesk_categories_to_merge = fields.Many2many(
        comodel_name='helpdesk.ticket.category', required=True)
    helpdesk_category_destination = fields.Many2one(
        comodel_name='helpdesk.ticket.category', required=True)

    send_emails = fields.Boolean(string="Send emails", default=False,
                                 help="Send email for each ticket when change "
                                      "category.")

    def merge_helpdesk_category(self):
        if not self.helpdesk_categories_to_merge:
            raise UserError(_('Helpdesk category to merge is empty.'))
        if not self.helpdesk_category_destination:
            raise UserError(_('Helpdesk category destination is empty.'))
        # All ticket of category to merge will be transfer
        lst_categories_to_merge = [a.id for a in self.helpdesk_categories_to_merge]
        lst_ticket = self.env["helpdesk.ticket"].search(
            [('category_id', 'in', lst_categories_to_merge)])
        for ticket in lst_ticket:
            ticket.with_context(mail_notrack=not self.send_emails).category_id = \
                self.helpdesk_category_destination.id

        self.env["helpdesk.ticket.category"].browse(
            lst_categories_to_merge).active = False
