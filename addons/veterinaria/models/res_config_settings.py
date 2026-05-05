from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    groq_api_key = fields.Char(
        string='Groq API Key',
        config_parameter='veterinaria.groq_api_key',
        help="Clave de API para Groq (Llama 3.1). Consíguela en console.groq.com"
    )
