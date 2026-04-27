from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class Turno(models.Model):
    _name = 'veterinaria.turno'
    _description = 'Modelo para representar un turno'

    mascota_id = fields.Many2one('veterinaria.mascota', string='Mascota')
    veterinario_id = fields.Many2one('res.users', string='Veterinarios')

    fecha_hora = fields.Datetime(string='Fecha de turno')

    estado = fields.Selection([
        ('draft', 'Borrador'),
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('done', 'Realizado'), 
        ('cancel', 'Cancelado'),
        ], default='draft', string="Estado")

    def action_confirm(self):
        for record in self:
            record.write({'estado': 'confirmed'})

    def action_done(self):
        for record in self:
            record.write({'estado': 'done'})

    def action_cancel(self):
        for record in self:
            record.write({'estado': 'cancel'})

    def iniciar_consulta(self):
        nuevo_historial = self.env['veterinaria.historial'].create({
            'mascota_id': self.mascota_id.id,
            'veterinario_id': self.veterinario_id.id,
            'fecha': fields.Datetime.now(), 
            'turno_id': self.id,
        })
        
        self.write({'estado': 'done'})
    
        return {
            'name': 'Historia Clínica',
            'type': 'ir.actions.act_window',
            'res_model': 'veterinaria.historial',
            'res_id': nuevo_historial.id,
            'view_mode': 'form',
            'target': 'current',
        }

    
    @api.constrains('fecha_hora', 'veterinario_id')
    def _check_fecha_hora(self):
        for record in self:
            if record.fecha_hora:
                fecha_min = record.fecha_hora - timedelta(minutes=30)
                fecha_max = record.fecha_hora + timedelta(minutes=30)

                existe_turno = self.env['veterinaria.turno'].search([
                    ('fecha_hora', '>', fecha_min),
                    ('fecha_hora', '<', fecha_max),
                    ('veterinario_id', '=', record.veterinario_id.id),
                    ('id', '!=', record._origin.id)
                ])
                if existe_turno:
                    raise ValidationError('Ya existe un turno para esta fecha y veterinario')