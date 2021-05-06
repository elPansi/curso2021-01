from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class HelpdeskTicketAction(models.Model):
    _name = 'helpdesk.ticket.action'
    _description = 'Action'
    _inherit = ['mail.thread.cc',
                'mail.thread.blacklist',

                'mail.activity.mixin' ]
    _primary_email = 'email_from'

    name = fields.Char(string='Name')
    date = fields.Date(default=datetime.today())
    time = fields.Float(string='Time', )
    ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Ticket')
    

class HelpdeskTicketTag(models.Model):
    _name = 'helpdesk.ticket.tag'
    _description = 'Tag'


    name = fields.Char(string='Name', required=True)
    public = fields.Boolean()
    tickets_ids = fields.Many2many(
        comodel_name='helpdesk.ticket',
        relation='helpdesk_ticket_tag_rel',
        column1='tag_id',
        column2='ticket_id',
        string='Tickets'
    )
    @api.model
    def cron_delete_tag(self):
        tags = self.search([('tickets_ids', '=', False)])
        tags.unlink()

    @api.model_create_multi
    def create(self, vals):
        res = super(HelpdeskTicketTag, self).create(vals)
        return res

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Ticket'

    def _date_default_today(self):
        return fields.Date.today()

    @api.model
    def default_get(self, default_fields):
        vals = super(HelpdeskTicket, self).default_get(default_fields)
        vals.update({'date': fields.Date.today() + timedelta(days=1) })
        return vals

    name = fields.Char(string='Name', required = True)
    description = fields.Text(string='Description', translate=True)
    date = fields.Date(default=_date_default_today)
    sequence = fields.Integer()
    state = fields.Selection(
        [('nuevo', 'Nuevo'), #valor bd, valor en la vista
        ('asignado', 'Asignado'),
        ('proceso', 'En proceso'),
        ('pendiente', 'Pendiente'),
        ('resuelto', 'Resuelto'),
        ('cancelado', 'Cancelado')],
        string='State',
        default='nuevo')

    #time = fields.Float(string='Time', )
    time = fields.Float(
        string='Time',
        compute='_get_time',
        inverse='_set_time',
        search='_search_time',
        store=True )
    #assigned = fields.Boolean(string='Assigned', readonly=True)

    assigned = fields.Boolean(
        string='Assigned',
        compute='_compute_assigned')

    date_limit = fields.Date(string='Date Limit' )
    action_corrective = fields.Html(
        string="Corrective Action",
        help='Descrive corrective actions to do')
    action_preventive = fields.Html(
        string="Preventive Action",
        help='Descrive corrective actions to do')

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned to')

    action_ids = fields.One2many(
        comodel_name='helpdesk.ticket.action',
        inverse_name='ticket_id',
        string='Actions')

    tag_ids = fields.Many2many(
        comodel_name='helpdesk.ticket.tag',
        relation='helpdesk_ticket_tag_rel',
        column1='ticket_id',
        column2='tag_id',
        string='Tags'
    )

    tag_name = fields.Char(
        string='Tag Name')

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')

    email_from = fields.Char(string='Email from')
    
    # #Ejemplo
    # @api.model
    # def close_leeds(self):
    #     active_tickets = self.search(['active', '=', True])

    #     for ticket in active_tickets:
    #         ticket.close()

    @api.depends('action_ids.time')
    def _get_time(self):
        for record in self:
            record.time = sum(record.action_ids.mapped('time'))


    def _set_time(self):
        for record in self:
            time_now = sum(record.action_ids.mapped('time'))
            next_time = record.time - time_now
            if next_time:
                data = {'name': '/', 'time': next_time, 'date': fields.Date.today(), 'ticket_id': record.id}
                self.env['helpdesk.ticket.action'].create(data)

    def _search_time(self, operator, value):
        ticket_action_groupby = self.env['helpdesk.ticket.action'].search(['time', operator, value])
        return [('id', 'in', actions.mapped('ticket_id').ids)]

    def asignar(self):
        self.ensure_one()
        # self.assigned = True
        # self.state = "asignado"
        self.write({
            'state': 'asignado', #¿Esto por que no lo hace?
            'assigned': True})
        # for ticket in self:
        #     ticket.state = 'asignado'  #¿Esto por que no lo hace?
        #     ticket.assigned = True

    def proceso(self):
        self.ensure_one()
        self.state = 'proceso'

    def pendiente(self):
        self.ensure_one()
        self.state = 'pendiente'

    def finalizar(self):
        self.ensure_one()
        self.state = 'resuelto'

    def cancelar(self):
        self.ensure_one()
        self.state = 'cancelado'

    def cancelar_multi(self):
        for record in self:
            record.cancelar()

    def do_recover(self):
        self.ensure_one()
        self.state = 'proceso'

    @api.depends('user_id')
    def _compute_assigned(self):
        for record in self:
            record.assigned= self.user_id and True or False


    ticket_qty = fields.Integer(
        string='Ticket Qty',
        compute='_compute_ticket_qty')

    @api.depends('user_id')
    def _compute_ticket_qty(self):
        for record in self:
            other_tickets = self.env['helpdesk.ticket'].search([('user_id', '=', record.user_id.id)])
            record.ticket_qty = len(other_tickets)

    def create_tag(self):
        self.ensure_one()
        #import pdb; pdb.set_trace()
        #import wdb; wdb.set_trace()
        # opción 1
        # self.write({
        #     'tag_ids': [(0, 0, {'name': self.tag_name})]
        # })
        # self.tag_name = False
        # # opcion 2
        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name': self.tag_name
        # })
        # self.write({
        #     'tag_ids': [(4, tag.id, 0)]
        # })
        # # opcion 3
        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name': self.tag_name
        # })
        # self.write({
        #     'tag_ids': [(6, 0, tag.ids)]
        # })
        # # opción 4
        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name': self.tag_name,
        #     'ticket_ids': [(6, 0, self.ids)]
        # })
        # # opción a través de action
        action = self.env.ref('helpdesk_fernandohernandez.action_new_tag').read()[0]
        action['context'] = {
            'default_name': self.tag_name,
            'default_tickets_ids': [(6, 0, self.ids)]
            # ¿es default_ticket_ids o default_tickets_ids?
        }
        self.tag_name = False
        return action

    @api.constrains('time')
    def _time_positive(self):
        for ticket in self:
            if ticket.time and ticket.time < 0:
                raise ValidationError(_("Time can not be negative"))

    @api.onchange('date', 'time')
    def _onchange_date(self):
        self.date_limit = self.date and self.date + timedelta(hours=self.time)



    # @api.onchange('date_limit')
    # def _onchangedate_limit(self):
    #     date_limit = self.date and self.date + timedelta(days=1)
    #     self.date_limit = date_limit