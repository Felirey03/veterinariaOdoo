from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
import urllib.parse
import logging
_logger = logging.getLogger(__name__)

class Turno(models.Model):
    _name = 'veterinaria.turno'
    _description = 'Modelo para representar un turno'

    mascota_id = fields.Many2one('veterinaria.mascota', string='Mascota', required=True)
    veterinario_id = fields.Many2one('res.users', string='Veterinario', required=True)

    fecha_hora = fields.Datetime(string='Fecha de turno', required=True)

    estado = fields.Selection([
        ('draft', 'Borrador'),
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('in_consultation', 'En Consulta'),
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
        self.write({'estado': 'in_consultation'})
        return {
            'name': 'Historial Clínico',
            'type': 'ir.actions.act_window',
            'res_model': 'veterinaria.historial',
            'res_id': nuevo_historial.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_whatsapp_reminder(self):
        """Abre un link de WhatsApp con un mensaje generado por IA o pre-cargado."""
        self.ensure_one()
        if not self.mascota_id:
            raise ValidationError("El turno no tiene una mascota asignada.")
        if not self.fecha_hora:
            raise ValidationError("El turno no tiene una fecha asignada.")
        if not self.mascota_id.propietario_id.mobile and not self.mascota_id.propietario_id.phone:
            raise ValidationError("El propietario no tiene un número de teléfono configurado.")

        # Intentar obtener la API Key de Groq desde los parámetros del sistema
        api_key = self.env['ir.config_parameter'].sudo().get_param('veterinaria.groq_api_key')
        _logger.info("GROG API KEY ENCONTRADA: %s", bool(api_key))
        
        phone = self.mascota_id.propietario_id.mobile or self.mascota_id.propietario_id.phone
        phone = "".join(filter(str.isdigit, phone))
        fecha_local = fields.Datetime.context_timestamp(self, self.fecha_hora)
        fecha_formateada = fecha_local.strftime('%d/%m/%Y %H:%M')

        mensaje = ""
        if api_key:
            try:
                
                from groq import Groq
                client = Groq(api_key=api_key)
                
                #Prompt para la IA
                prompt = f"""
                Actúa como un asistente administrativo de una clínica veterinaria. 
                Genera un mensaje de WhatsApp para recordar un turno.
                
                DATOS:
                - Dueño: {self.mascota_id.propietario_id.name}
                - Mascota: {self.mascota_id.name}
                - Fecha y Hora: {fecha_formateada}
                - Peso actual de la mascota: {self.mascota_id.ultimo_peso} kg
                
                REGLAS:
                - Tono: Muy informal y cálido, pero profesional.
                - Sé breve y claro.
                - Menciona a la mascota por su nombre.
                - El mensaje debe ser en español.
                - No uses emojis excesivos.
                """
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=150,
                )
                mensaje = completion.choices[0].message.content.strip()
                
            except Exception as e:
                
                #Esto es por si falla la IA el mensaje por defecto!
                mensaje = (
                    f"Hola {self.mascota_id.propietario_id.name}! Te recordamos el turno de "
                    f"{self.mascota_id.name} para el día {fecha_formateada}. ¡Te esperamos!"
                )
        else:
            #Mensaje por defecto si no hay API Key
            mensaje = (
                f"Hola {self.mascota_id.propietario_id.name}! Te escribimos de la Veterinaria para recordarte "
                f"el turno de {self.mascota_id.name} para el día {fecha_formateada}. Te esperamos!"
            )

        mensaje_encoded = urllib.parse.quote(mensaje)
        url = f"https://wa.me/{phone}?text={mensaje_encoded}"

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
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