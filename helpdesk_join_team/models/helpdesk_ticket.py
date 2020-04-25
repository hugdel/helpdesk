# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import werkzeug

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    show_create_employee = fields.Boolean(compute="_compute_show_create_employee",
                                          readonly=True)
    is_employee = fields.Boolean(string="is_employee", default=False)

    @api.multi
    @api.depends('category_id', 'partner_id')
    def _compute_show_create_employee(self):
        data_category_join_team = self.env.ref(
            'helpdesk_join_team.helpdesk_ticket_category_join_team').id
        for val in self:
            if data_category_join_team != val.category_id.id:
                val.show_create_employee = False
            else:
                if val.partner_id:
                    res = self.env['hr.employee'].search(
                        [("work_email", "=", self.partner_id.email)])
                    val.show_create_employee = not res
                else:
                    val.show_create_employee = True

    def send_join_team_mail(self):
        if self.partner_email:
            self.env.ref('helpdesk_join_team.join_team_email_template'). \
                send_mail(self.id, email_values={}, force_send=True)

    @api.model_create_multi
    def create(self, vals_list):
        res_list = super(HelpdeskTicket, self).create(vals_list)

        for res in res_list:

            if res.category_id.id == self.env.ref(
                    'helpdesk_join_team.helpdesk_ticket_category_join_team').id:
                res.send_join_team_mail()

        return res

    def create_employee(self):
        if not self.partner_id:
            self.create_res_partner()

        # Check duplicate employee
        res = self.env['hr.employee'].search(
            [("work_email", "=", self.partner_id.email)])
        if res:
            raise UserError(_('An employee already exist with work_email "%s". '
                              'Check employee named "%s".') %
                            (self.partner_id.email, res[0].name))

        data_ref_category = self.env.ref(
            'helpdesk_join_team.helpdesk_ticket_category_join_team')
        if self.category_id.id != data_ref_category.id:
            raise UserError(
                _('The category need to be "%s".') % data_ref_category.name)

        # Create res.user
        company_id = self.env['res.company']._company_default_get('res.users').id
        user_employee = self.sudo().with_context(company_id=company_id)._create_user(
            self.partner_id.email)
        user_employee.groups_id = [
            (6, 0, [self.env.ref('base.group_user').id])
        ]
        user_employee.user_ids.partner_id.signup_prepare()
        user_sudo = user_employee.user_ids

        template = self.env.ref(
            'auth_signup.mail_template_user_signup_account_created',
            raise_if_not_found=False)
        if user_sudo and template:
            template.sudo().with_context(
                lang=user_sudo.lang,
                auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
            ).send_mail(user_sudo.id, force_send=True)

        values = {
            "user_id": user_sudo.id,
            "work_email": self.partner_email,
            "work_phone": self.partner_phone,
            # "address_home_id": self.partner_address,
            # "image": self.partner_id.image,
            "name": self.partner_name,
        }

        self.env['hr.employee'].create(values)
        self.partner_id.customer = False
        self.is_employee = True

    @api.multi
    def _create_user(self, email):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        company_id = self.env.context.get('company_id')
        return self.env['res.users'].with_context(
            no_reset_password=True)._create_user_from_template({
            'email': email,
            'login': email,
            'partner_id': self.partner_id.id,
            'company_id': company_id,
            'company_ids': [(6, 0, [company_id])],
        })
