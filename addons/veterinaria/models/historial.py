from odoo import models, fields, api
from datetime import datetime

class HistorialClinico(models.Model):
    _name = 'veterinaria.historial'
    _description = 'Historial Clínico de Mascota'
    _order = 'fecha desc'

    name = fields.Char(string='Referencia', compute='_compute_name', store=True)
    fecha = fields.Datetime(string='Fecha de Consulta', default=fields.Datetime.now, required=True)
    
    
    mascota_id = fields.Many2one('veterinaria.mascota', string='Mascota', required=True, ondelete='cascade')
    propietario_id = fields.Many2one(related='mascota_id.propietario_id', string='Propietario', readonly=True)
    veterinario_id = fields.Many2one('res.users', string='Veterinario', default=lambda self: self.env.user, required=True)
    turno_id = fields.Many2one('veterinaria.turno', string='Turno Relacionado')

    
    peso = fields.Float(string='Peso (kg)', digits=(5, 2))
    temperatura = fields.Float(string='Temperatura (°C)', digits=(4, 1))
    frecuencia_cardiaca = fields.Integer(string='Frecuencia Cardíaca (lpm)')
    frecuencia_respiratoria = fields.Integer(string='Frecuencia Respiratoria (rpm)')

    
    subjetivo = fields.Html(string='Subjetivo (S)', help="Motivo de consulta y anamnesis reportada por el dueño.")
    objetivo = fields.Html(string='Objetivo (O)', help="Hallazgos del examen físico y pruebas diagnósticas.")
    evaluacion = fields.Html(string='Evaluación (A)', help="Diagnóstico clínico, presuntivo o diferencial.")
    plan = fields.Html(string='Plan (P)', help="Tratamiento, medicación, recomendaciones y seguimiento.")



    @api.depends('fecha', 'mascota_id')
    def _compute_name(self):
        for record in self:
            if record.fecha and record.mascota_id:
                fecha_str = record.fecha.strftime('%d/%m/%Y')
                record.name = f"Consulta: {record.mascota_id.name} ({fecha_str})"
            else:
                record.name = "Nueva Consulta"