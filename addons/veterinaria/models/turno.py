from odoo import models, fields

class Turno(models.Model):
    _name = 'veterinaria.turno'
    _description = 'Modelo para representar un turno'

    mascota_id = fields.Many2one('veterinaria.mascota', string='Mascota')
    veterinario_id = fields.Many2one('res.users', string='Veterinarios')

    fecha_hora = fields.Datetime(string='Fecha de turno')
    estado = fields.Boolean(string="Estado de turno")
