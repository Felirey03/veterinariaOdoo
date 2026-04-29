from odoo import models, fields, api

class Vacuna(models.Model):
    _name = 'veterinaria.vacuna'
    _description = 'Modelo para representar una vacuna'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(related="producto_id.name", string="Nombre de la Vacuna", store=True)
    mascota_id = fields.Many2one('veterinaria.mascota', string="Mascota", required=True)
    producto_id = fields.Many2one('product.product', string="Vacuna", required=True)

    fecha_aplicacion = fields.Date(string="Fecha de Aplicación", required=True)
    fecha_refuerzo = fields.Date(string="Fecha de Refuerzo")

    veterinario_id = fields.Many2one('res.users', string="Veterinario", default=lambda self: self.env.user)
    observaciones = fields.Text(string="Observaciones")

    def _crear_actividad_si_corresponde(self):
        """Crea una actividad de recordatorio si la vacuna vence en 7 días o menos y no tiene una ya."""
        today = fields.Date.today()
        limite = fields.Date.add(today, days=7)
        for v in self:
            if not v.fecha_refuerzo or not (today <= v.fecha_refuerzo <= limite):
                continue
            # Evitar duplicados: no creamos si ya existe una actividad con ese resumen
            ya_existe = self.env['mail.activity'].search_count([
                ('res_id', '=', v.id),
                ('res_model', '=', 'veterinaria.vacuna'),
                ('summary', 'ilike', 'Refuerzo de'),
            ])
            if not ya_existe:
                v.activity_schedule(
                    'mail.mail_activity_data_todo',
                    date_deadline=v.fecha_refuerzo,
                    summary=f"Refuerzo de {v.name} para {v.mascota_id.name}",
                    user_id=v.veterinario_id.id or self.env.user.id,
                )

    def cron_check_vacunas(self):
        """Proceso automático diario: revisa todas las vacunas próximas a vencer."""
        today = fields.Date.today()
        limite = fields.Date.add(today, days=7)
        vacunas = self.search([
            ('fecha_refuerzo', '>=', today),
            ('fecha_refuerzo', '<=', limite),
        ])
        vacunas._crear_actividad_si_corresponde()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._crear_actividad_si_corresponde()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'fecha_refuerzo' in vals:
            self._crear_actividad_si_corresponde()
        return res