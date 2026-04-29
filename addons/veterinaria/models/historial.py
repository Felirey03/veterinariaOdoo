from odoo import models, fields, api
from odoo.exceptions import ValidationError
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

    
    factura_id = fields.Many2one('account.move', string='Factura', readonly=True, copy=False)
    tiene_factura_activa = fields.Boolean(compute='_compute_tiene_factura_activa')

    @api.depends('factura_id', 'factura_id.state')
    def _compute_tiene_factura_activa(self):
        for record in self:
            record.tiene_factura_activa = bool(record.factura_id and record.factura_id.state != 'cancel')

    @api.depends('fecha', 'mascota_id')
    def _compute_name(self):
        for record in self:
            if record.fecha and record.mascota_id:
                fecha_str = record.fecha.strftime('%d/%m/%Y')
                record.name = f"Consulta: {record.mascota_id.name} ({fecha_str})"
            else:
                record.name = "Nueva Consulta"

    def action_crear_factura(self):
        self.ensure_one()
        if not self.propietario_id:
            raise ValidationError("No se puede facturar porque la mascota no tiene un propietario asignado.")
        if self.tiene_factura_activa:
            return
        factura = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.propietario_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': self.name,
                'quantity': 1,
                'price_unit': 0,
            })],
        })
        self.factura_id = factura.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': factura.id,
            'target': 'current',
        }