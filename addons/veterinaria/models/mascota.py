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

    vacuna_ids = fields.One2many('veterinaria.vacuna', 'mascota_id')
    tiene_vacunas_vencidas = fields.Boolean(compute='_compute_tiene_vacunas_vencidas')

    @api.depends('vacuna_ids.fecha_refuerzo')
    def _compute_tiene_vacunas_vencidas(self):
        today = fields.Date.today()
        for record in self:
            # Buscamos si alguna vacuna del historial tiene fecha de refuerzo anterior o igual a hoy
            vencidas = record.vacuna_ids.filtered(lambda v: v.fecha_refuerzo and v.fecha_refuerzo <= today)
            record.tiene_vacunas_vencidas = bool(vencidas)

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