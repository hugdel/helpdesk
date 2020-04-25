import logging
from odoo import _, fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MassMailingScheduleDate(models.TransientModel):
    _name = 'helpdesk.mass.mailing.wizard'
    _description = 'Helpdesk add email to Mass Mailing'

    @api.model
    def default_get(self, fields):
        result = super(MassMailingScheduleDate, self).default_get(fields)

        helpdesk_ticket_ids = self.env.context.get('active_ids', [])
        helpdesk_ticket_ids_size = len(helpdesk_ticket_ids)
        result["number_of_contact"] = helpdesk_ticket_ids_size
        lst_helpdesk_ticket = self.env['helpdesk.ticket'].sudo().browse(
            helpdesk_ticket_ids)
        if helpdesk_ticket_ids_size > 1:
            # Validate all helpdesk_ticket is valid
            for ticket in lst_helpdesk_ticket:
                self._get_name_and_email_from_ticket(ticket)
        elif helpdesk_ticket_ids_size == 1:
            ticket = lst_helpdesk_ticket[0]
            name, email = self._get_name_and_email_from_ticket(ticket)
            result['name'] = name
            result['email'] = email
        else:
            raise UserError(_('Missing helpdesk ticket selection.'))
        result["helpdesk_ticket_id"] = helpdesk_ticket_ids

        lst_total_mml_id = []

        for ticket in lst_helpdesk_ticket:
            # mass_mailing_list domain exclude actual mail
            lst_mml_id_all = set(
                [a.id for a in self.env["mail.mass_mailing.list"].search([])])
            lst_mml_id_diff = set(
                [a.id for a in self.env["mail.mass_mailing.list"].search([])
                 for b in a.subscription_contact_ids if
                 b.contact_id.email == ticket.partner_email])
            lst_mml_id = list(lst_mml_id_all - lst_mml_id_diff)
            lst_total_mml_id = list(set(lst_total_mml_id + lst_mml_id))

        # result["mass_mailing_list_default"] = [(6, 0, lst_total_mml_id)]
        result["cache_mml"] = ";".join(
            [str(a) for a in lst_total_mml_id])
        return result

    email = fields.Char(string="Email")
    name = fields.Char(string="Name")
    number_of_contact = fields.Integer(string="Number of contact", readonly=True)
    helpdesk_ticket_id = fields.Many2many(comodel_name='helpdesk.ticket')

    cache_mml = fields.Char(string="Cache mass mailing domain.")
    # TODO this way with many2many not working, got error with duplicated key
    # mass_mailing_list_default = fields.Many2many(
    #     comodel_name='mail.mass_mailing.list',
    # )

    mass_mailing_list = fields.Many2many(
        comodel_name='mail.mass_mailing.list',
        # domain=[("id", "in", mass_mailing_list_default)]
    )

    @staticmethod
    def _get_name_and_email_from_ticket(ticket):
        """

        :return: (name, email)
        """
        if ticket.partner_name:
            name = ticket.partner_name
        elif ticket.partner_id and ticket.partner_id.name:
            name = ticket.partner_id.name
        else:
            raise UserError(_('Missing the partner name in ticket %s-"%s".') % (
                ticket.number, ticket.name))

        if ticket.partner_email:
            email = ticket.partner_email
        elif ticket.partner_id and ticket.partner_id.email:
            email = ticket.partner_id.email
        else:
            raise UserError(_('Missing the partner email in ticket %s-"%s".') % (
                ticket.number, ticket.name))

        return name, email

    @api.onchange('mass_mailing_list')
    def onchange_mass_mailing_list(self):
        # res = {'domain': {
        #     'mass_mailing_list': [('id', 'in', self.mass_mailing_list_default.ids)],
        # }
        # }
        lst_mass_mailing = self.cache_mml.split(
            ";") if self.cache_mml else []

        res = {'domain': {
            'mass_mailing_list': [('id', 'in', lst_mass_mailing)],
        }
        }
        return res

    def set_mailing_list(self):
        for ticket in self.helpdesk_ticket_id:
            name, email = self._get_name_and_email_from_ticket(ticket)
            self._set_contact_mailing_list(name, email)

    def _set_contact_mailing_list(self, name, email):
        for mailing_list in self.mass_mailing_list:
            lst_find = [a for a in mailing_list.subscription_contact_ids if
                        a.contact_id.email == email]
            if lst_find:
                # Do not duplicate mailing list contact
                _logger.warning(
                    "Cannot add email '%s' on mailing list '%s', already exist." % (
                        email, mailing_list.name))
                return

            # Search contact to use it, else create it
            contact_ids = self.env['mail.mass_mailing.contact'].search(
                [('email', '=', email)])

            if not contact_ids:
                values = {
                    "email": email,
                    "name": name,
                }
                contact_id = self.env['mail.mass_mailing.contact'].create(values)
            else:
                if len(contact_ids) > 1:
                    lst_name = [c.name for c in contact_ids]
                    _logger.warning(
                        "Duplicated mail.mass_mailing.contact '%s' - '%s'" % (
                            email, lst_name))
                contact_id = contact_ids[0]

            values = {
                "opt_out": False,
                "list_id": mailing_list.id,
                "unsubscription_date": False,
                "contact_id": contact_id.id,
            }
            self.env['mail.mass_mailing.list_contact_rel'].create(values)
