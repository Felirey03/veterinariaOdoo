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
    historial_ids = fields.One2many('veterinaria.historial', 'mascota_id', string='Historias Clínicas')
    tiene_vacunas_vencidas = fields.Boolean(compute='_compute_tiene_vacunas_vencidas', store=True)
    ultimo_peso = fields.Float(string='Último Peso', compute='_compute_ultimo_peso', store=True)
    ia_insights = fields.Html(string="Análisis de Tendencias (IA)", help="Resumen inteligente de salud basado en el historial.")
    ia_insights_last_update = fields.Datetime(string="Última actualización de IA")
    ultimo_historial_analizado_id = fields.Many2one('veterinaria.historial', string="Último Historial Analizado")

    @api.depends('historial_ids.peso', 'historial_ids.fecha')
    def _compute_ultimo_peso(self):
        for mascota in self:
            historial = self.env['veterinaria.historial'].search([
                ('mascota_id', '=', mascota.id),
                ('peso', '>', 0)
            ], order='fecha desc', limit=1)
            mascota.ultimo_peso = historial.peso if historial else 0.0

    def action_generate_ia_insights(self, force=False):
        """Analiza los últimos historiales para encontrar patrones, solo si hay datos nuevos."""
        self.ensure_one()
        api_key = self.env['ir.config_parameter'].sudo().get_param('veterinaria.groq_api_key')
        if not api_key:
            return
        
        # Obtener el historial más reciente para ver si cambió algo
        ultimo_h = self.env['veterinaria.historial'].search([
            ('mascota_id', '=', self.id)
        ], order='fecha desc', limit=1)

        if not ultimo_h:
            self.ia_insights = "<p>No hay suficiente historial para realizar un análisis.</p>"
            return

        # Si no hay historiales nuevos y no estamos forzando, no hacemos nada
        if not force and self.ultimo_historial_analizado_id == ultimo_h:
            return

        # Obtenemos los últimos 5 historiales para el análisis
        historiales = self.env['veterinaria.historial'].search([
            ('mascota_id', '=', self.id)
        ], order='fecha desc', limit=5)

        # Preparamos los datos para la IA
        datos_clinicos = []
        for h in historiales:
            datos_clinicos.append({
                'fecha': h.fecha.strftime('%d/%m/%Y'),
                'peso': h.peso,
                'evaluacion': h.evaluacion if h.evaluacion else '',
                'plan': h.plan if h.plan else ''
            })

        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            
            prompt = f"""
            Actúa como un Auditor Clínico Veterinario. Tu trabajo es detectar patrones en los datos, NO dar consejos médicos.
            
            PACIENTE: {self.name}
            DATOS CRONOLÓGICOS: {datos_clinicos}
            
            REGLAS CRÍTICAS:
            1. PROHIBIDO dar sugerencias, recomendaciones de tratamiento o diagnósticos nuevos.
            2. FÓCATE solo en hechos extraídos de la comparación de datos.
            3. NO uses la palabra 'IA' ni 'Estratégico' en el texto.
            
            REGLAS DE FORMATO (HTML):
            - Título general: <h3 style='color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;'>Resumen de Evolución Clínica</h3>
            - Títulos de sección: <h4 style='color: #2980b9; margin-top: 20px; font-weight: bold;'>[Nombre Sección]</h4>
            - Listas: <ul> con <li> bien espaciados.
            - Alertas: Usa <span style='color: #c0392b; font-weight: bold;'> para resaltar alertas críticas de datos.
            
            SECCIONES A COMPLETAR:
            1. Evolución de Peso: Compara pesos entre fechas y calcula variaciones (%) reales.
            2. Patrones Recurrentes: Identifica si un síntoma o motivo se repite en el tiempo.
            3. Alertas de Datos: Identifica si hay incoherencias o datos que el médico deba notar (Ej: tiempo prolongado con un fármaco según el historial).
            
            Idioma: Español.
            """

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0, # Determinismo máximo
            )

            self.write({
                'ia_insights': completion.choices[0].message.content,
                'ia_insights_last_update': fields.Datetime.now(),
                'ultimo_historial_analizado_id': ultimo_h.id
            })
        except Exception:
            pass 

    @api.depends('vacuna_ids.fecha_refuerzo')
    def _compute_tiene_vacunas_vencidas(self):
        today = fields.Date.today()
        for record in self:
            #Buscamos si alguna vacuna del historial tiene fecha de refuerzo anterior o igual a hoy
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
                    #Calculo simple de meses si es menor de un año
                    meses = (today.year - record.fecha_nacimiento.year) * 12 + (today.month - record.fecha_nacimiento.month)
                    record.edad = f"{meses} meses"
            else:
                record.edad = "Desconocida"