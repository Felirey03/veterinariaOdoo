from odoo import models, fields

class Mascota(models.Model):
    _name = 'veterinaria.mascota'
    _description = 'Modelo para representar una mascota'

    name = fields.Char(string='Nombre', required=True)

    edad = fields.Integer(string='Edad')

    propietario_id = fields.Many2one('res.partner', string='Propietario')

    especie = fields.Selection([
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('ave', 'Ave'),
        ('otro', 'Otro'),
    ], string='Especie')

    