import logging
import werkzeug
import odoo.http as http
import base64
from openerp.http import request
import sys
import os

# Add path to support inherit helpdesk_mgmt_controllers_main.HelpdeskTicketController
# inherit not working with http.Controller
# TODO fix the path when moving modules in OCA_helpdesk
new_path = os.path.normpath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'OCA_helpdesk',
                 'helpdesk_mgmt'))
sys.path.append(new_path)
from controllers import main as helpdesk_mgmt_controllers_main

_logger = logging.getLogger(__name__)


class HelpdeskTicketController(helpdesk_mgmt_controllers_main.HelpdeskTicketController):
    @http.route('/new/ticket', type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        # Find parent company
        partner_id = http.request.env.user.partner_id
        # Find root of company and support max 100 levels
        i = 0
        parent_id = partner_id.parent_id
        while i < 100 and parent_id and parent_id.parent_id:
            i += 1
            parent_id = parent_id.parent_id
        if not parent_id:
            parent_id = partner_id

        categories = http.request.env['helpdesk.ticket.category']. \
            search([('active', '=', True)], order="name")

        # Special case, move at the end the option "other" of affected_systems
        affected_systems = http.request.env['helpdesk.ticket.affected_system'].search(
            [('active', '=', True), ('name', '!=', 'Other')], order="name") + \
                           http.request.env[
                               'helpdesk.ticket.affected_system'].search(
                               [('active', '=', True), ('name', '=', 'Other')])

        filter_responsibles = [('active', '=', True),
                               ('commercial_partner_id', '=', parent_id.id),
                               ('type', '=', 'contact')]
        if parent_id.id != partner_id.id:
            filter_responsibles.append(('id', '!=', parent_id.id))

        responsibles = http.request.env['res.partner'].search(filter_responsibles,
                                                              order="name")

        filter_localisations = [('active', '=', True),
                                ('commercial_partner_id', '=', parent_id.id),
                                ('type', 'in', ('other', 'delivery'))]
        localisations = parent_id + http.request.env['res.partner'].search(
            filter_localisations, order="name")

        filter_invoice = [('active', '=', True),
                          ('commercial_partner_id', '=', parent_id.id),
                          ('type', '=', 'invoice')]
        localisations_invoice = parent_id + http.request.env['res.partner'].search(
            filter_invoice, order="name")

        email = http.request.env.user.email
        phone = http.request.env.user.phone if http.request.env.user.phone else http.request.env.user.mobile
        reporter = http.request.env.user.name

        return http.request.render('helpdesk_mgmt.portal_create_ticket', {
            'partner_id': partner_id,
            'categories': categories,
            'categories_size': len(categories),
            'affected_systems': affected_systems,
            'email': email,
            'phone': phone,
            'reporter': reporter,
            'root_partner_id': parent_id,
            'responsibles': responsibles,
            'localisations': localisations,
            'localisations_invoice': localisations_invoice,
        })

    @http.route('/submitted/ticket',
                type="http", auth="user", website=True, csrf=True)
    def submit_ticket(self, **kw):
        partner_id = http.request.env['res.partner'].browse(int(kw.get("responsible")))
        vals = {
            'partner_name': partner_id.name,
            'company_id': http.request.env.user.company_id.id,
            'category_id': kw.get('category'),
            # 'partner_email': kw.get('email'),
            # 'partner_phone': kw.get('phone'),
            'description': kw.get('description'),
            'name': kw.get('subject'),
            'attachment_ids': False,
            'channel_id':
                request.env['helpdesk.ticket.channel'].sudo().search(
                    [('name', '=', 'Portal')]).id,
            'partner_id': partner_id.id,
            'partner_address': http.request.env['res.partner'].browse(
                int(kw.get("localisation"))).street,
            'partner_address_invoice': http.request.env['res.partner'].browse(
                int(kw.get("invoice_address"))).street,
            'problem_location': kw.get("problem_location"),
            'affected_system_id': kw.get("affected_system"),
            'team_id': kw.get("team_id"),
            'severity': kw.get("severity"),
        }
        new_ticket = request.env['helpdesk.ticket'].sudo().create(vals)

        subscriber = request.env.user.partner_id.ids
        if partner_id.id not in subscriber:
            subscriber.append(partner_id.id)
        new_ticket.message_subscribe(subscriber)
        if kw.get('attachment'):
            for c_file in request.httprequest.files.getlist('attachment'):
                data = c_file.read()
                if c_file.filename:
                    request.env['ir.attachment'].sudo().create({
                        'name': c_file.filename,
                        'datas': base64.b64encode(data),
                        'datas_fname': c_file.filename,
                        'res_model': 'helpdesk.ticket',
                        'res_id': new_ticket.id
                    })
        return werkzeug.utils.redirect("/my/tickets")
