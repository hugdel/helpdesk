from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo import api, SUPERUSER_ID


class WebsiteForm(WebsiteForm):

    def insert_record(self, request, model, values, custom, meta=None):
        if model.model == 'helpdesk.ticket':
            with api.Environment.manage():
                env = api.Environment(request.cr, SUPERUSER_ID, {})
                if 'channel_id' not in values:
                    values['channel_id'] = env.ref("helpdesk_mgmt.helpdesk_ticket_channel_web").id
        return super(WebsiteForm, self).insert_record(request, model, values, custom, meta=meta)
