from odoo import models, fields, api
from datetime import datetime


class HelpdeskTicketAction(models.Model):
    _name = 'helpdesk.ticket.action'
    _description = 'Action'

    name = fields.Char(string='Name')    
    date = fields.Date(default=datetime.today())

    ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Ticket')

class HelpdeskTicketTag(models.Model):
    _name = 'helpdesk.ticket.tag'
    _description = 'Tag'


    name = fields.Char(string='Name', required = True)    

    tickets_ids = fields.Many2many(
        comodel_name='helpdesk.ticket',
        relation='helpdesk_ticket_tag_rel',
        column1='tag_id',
        column2='ticket_id',
        string='Tags'
    )


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Ticket'

    name = fields.Char(string='Name', required = True)
    description = fields.Text(string='Description', translate=True)
    date = fields.Date(default=datetime.today())
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

    time = fields.Float(string='Time', )

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

    # #Ejemplo
    # @api.model
    # def close_leeds(self):
    #     active_tickets = self.search(['active', '=', True])
        
    #     for ticket in active_tickets:
    #         ticket.close()

    def asignar(self):
        self.ensure_one()
        # self.write({
        #     'state': 'asignado', #¿Esto por que no lo hace?
        #     'assigned': True})
        for ticket in self: 
            ticket.state = 'asignado'  #¿Esto por que no lo hace?
            ticket.assigned = True
    
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
        # opción 1
        self.write({
            'tag_ids': [(0, 0, {'name': self.tag_name})]
        })
        self.tag_name = False
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

        
    