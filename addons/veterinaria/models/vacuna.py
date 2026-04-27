from odoo import models, fields, api

class Vacuna(models.Model):
    _name = 'veterinaria.vacuna'
    _description = 'Modelo para representar una vacuna'

    name = fields.Char(related="producto_id.name", string="Nombre de la Vacuna", store=True)
    mascota_id = fields.Many2one('veterinaria.mascota', string="Mascota", required=True)
    producto_id = fields.Many2one('product.product', string="Vacuna", required=True)
    
    fecha_aplicacion = fields.Date(string="Fecha de Aplicación", required=True)
    fecha_refuerzo = fields.Date(string="Fecha de Refuerzo")
    
    veterinario_id = fields.Many2one('res.users', string="Veterinario", default=lambda self: self.env.user)
    observaciones = fields.Text(string="Observaciones")

    