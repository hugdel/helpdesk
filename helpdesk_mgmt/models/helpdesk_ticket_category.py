from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HelpdeskCategory(models.Model):
    _name = 'helpdesk.ticket.category'
    _description = 'Helpdesk Ticket Category'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )

    @api.multi
    def unlink(self):
        dct_undeleted_categories = {a.res_id: a for a in
                                    self.env["ir.model.data"].sudo().search(
                                        [('model', '=', 'helpdesk.ticket.category')])}
        for category in self:
            if category.id in dct_undeleted_categories.keys():
                undeleted_category = dct_undeleted_categories.get(category.id)
                raise UserError(_('Cannot delete category %s, '
                                  'because is required by module.\nKey : %s') %
                                (undeleted_category.model,
                                 "\n".join([f"'{a.res_id} {a.complete_name}'" for a in
                                           dct_undeleted_categories.values()])))
        return super().unlink()
