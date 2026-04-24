from odoo import models, fields, api

class Mascota(models.Model):
    _name = 'veterinaria.mascota'
    _description = 'Modelo para representar una mascota'

    name = fields.Char(string='Nombre', required=True)

    propietario_id = fields.Many2one('res.partner', string='Propietario')
    
    especie = fields.Selection([
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('ave', 'Ave'),
        ('otro', 'Otro'),
    ], string='Especie')

    sexo = fields.Selection([
        ('macho', 'Macho'),
        ('hembra', 'Hembra'),
    ], string='Sexo')

    raza = fields.Char(string='Raza')
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento')
    edad = fields.Char(string='Edad', compute='_compute_edad', store=False)
    alerta_medica = fields.Text(string='Alerta Médica / Alergias', help="Información crítica que debe verse rápido.")

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        for record in self:
            if record.fecha_nacimiento:
                today = fields.Date.today()
                diff = today.year - record.fecha_nacimiento.year - ((today.month, today.day) < (record.fecha_nacimiento.month, record.fecha_nacimiento.day))
                if diff > 0:
                    record.edad = f"{diff} años"
                else:
                    # Cálculo simple de meses si es menor de un año
                    meses = (today.year - record.fecha_nacimiento.year) * 12 + (today.month - record.fecha_nacimiento.month)
                    record.edad = f"{meses} meses"
            else:
                record.edad = "Desconocida"