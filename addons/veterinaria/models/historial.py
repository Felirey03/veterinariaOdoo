from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

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
    turno_estado = fields.Selection(related='turno_id.estado', string='Estado del Turno', readonly=True)

    
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
    es_sugerencia_ia = fields.Boolean(string="Generado por IA", default=False)
    alerta_medica_rel = fields.Text(related='mascota_id.alerta_medica', string="Alerta Médica de Mascota")
    ia_insights_rel = fields.Html(related='mascota_id.ia_insights', string="Tendencias de Salud")

    @api.depends('factura_id', 'factura_id.state')
    def _compute_tiene_factura_activa(self):
        for record in self:
            record.tiene_factura_activa = bool(record.factura_id and record.factura_id.state != 'cancel')

    def action_ai_clinical_help(self):
        """Usa IA para pulir y profesionalizar el SOAP completo."""
        self.ensure_one()
        api_key = self.env['ir.config_parameter'].sudo().get_param('veterinaria.groq_api_key')
        if not api_key:
            raise ValidationError("No se encontró la API Key de Groq.")
        
        # Verificamos si hay algo escrito en algún campo
        if not any([self.subjetivo, self.objetivo, self.evaluacion, self.plan]):
            raise ValidationError("Escribí algunas notas en cualquier campo para que pueda ayudarte a pulirlas.")

        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            
            prompt = f"""
            Actúa como un transcriptor médico veterinario profesional. Organiza mis notas en formato HTML elegante.
            
            REGLAS DE FORMATO (ESTRICTAS):
            - Usa listas con viñetas HTML (<ul><li>...</li></ul>) para separar ideas o síntomas.
            - Usa negritas HTML (<b>...</b>) para términos médicos importantes.
            - Usa saltos de línea (<br/>) si es necesario.
            - El resultado debe ser HTML limpio listo para un editor de texto enriquecido.
            - NO inventes datos.
            - Si el campo está vacío, déjalo vacío.
            
            NOTAS A PULIR:
            S (Subjetivo): {self.subjetivo}
            O (Objetivo): {self.objetivo}
            A (Evaluación): {self.evaluacion}
            P (Plan): {self.plan}
            ---
            Responde en formato JSON estrictamente:
            {{"subjetivo": "contenido html", "objetivo": "contenido html", "evaluacion": "contenido html", "plan": "contenido html"}}
            Idioma: Español.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={ "type": "json_object" }
            )
            
            import json
            # Logueamos la respuesta cruda para ver qué mandó
            _logger.info("CONTENIDO CRUDO IA: %s", completion.choices[0].message.content)
            
            res_json = json.loads(completion.choices[0].message.content)
            
            # Normalizamos claves a minúsculas por si la IA se puso creativa
            res_norm = {k.lower(): v for k, v in res_json.items()}
            
            self.write({
                'subjetivo': res_norm.get('subjetivo', self.subjetivo),
                'objetivo': res_norm.get('objetivo', self.objetivo),
                'evaluacion': res_norm.get('evaluacion', self.evaluacion),
                'plan': res_norm.get('plan', self.plan),
                'es_sugerencia_ia': True
            })
            
            return True
            
        except Exception as e:
            raise ValidationError(f"Error con la IA: {str(e)}")

    def action_refresh_ia_insights(self):
        """Dispara el análisis de tendencias en la mascota vinculada de forma forzada."""
        self.ensure_one()
        if self.mascota_id:
            self.mascota_id.action_generate_ia_insights(force=True)
        return True
        
        return True

    def action_finalizar_consulta(self):
        self.ensure_one()
        if self.turno_id:
            self.turno_id.action_done()
        return True

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