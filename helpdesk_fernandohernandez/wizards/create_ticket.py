from odoo import models, api, fields, _

class ModelName(models.TransientModel):
    _name = 'create.ticket'

    name = fields.Char()

    def create_ticket(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        if active_id and  self._context.get('active_model') == 'helpdesk.ticket.tag':
            ticket = self.env['helpdesk.ticket'].create({
                'name': self.name,
                'tag_ids': [(6, 0, [active_id])]
            })
            action = self.env.ref('helpdesk_fernandohernandez.helpdesk_ticket_action').read()[0]
            action['res_id'] = ticket.id
            action['views'] = [(self.env.ref('helpdesk_fernandohernandez.view_helpdesk_ticket_form').id, 'form')]
            return(action)
        return {'type': 'ir.actions.act_window_close'} 

    