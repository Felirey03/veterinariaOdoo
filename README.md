# Sistema de Gestión para Veterinaria - Odoo 17

Este proyecto nace como una práctica personal para seguir aprendiendo desarrollo en Odoo, pero con la idea de resolver un caso real: la gestión básica de una veterinaria.

La idea principal es evitar procesos manuales o en papel y llevar todo a un sistema simple, ordenado y escalable.

## ¿Qué incluye por ahora?

Actualmente el módulo es una herramienta clínica funcional:

- **Gestión de Mascotas**: Ficha enriquecida con raza, sexo, fecha de nacimiento y alertas médicas.
- **Cómputo Automático de Edad**: Cálculo dinámico en años o meses según la edad del paciente.
- **Historial Clínico (EMR)**: Registro estructurado bajo formato **SOAP** (Subjetivo, Objetivo, Evaluación, Plan) con seguimiento de signos vitales.
- **Gestión de Turnos**: Ciclo de vida (Borrador, Confirmado, Realizado), validación de solapamientos y vista de calendario.
- **Relación Dueño-Mascota**: Vinculación directa con contactos (`res.partner`) de Odoo.

## En qué estoy trabajando ahora

El foco se desplaza hacia la optimización del flujo de trabajo:

1.  **Automatización de Consulta**: Botón para convertir turnos realizados en entradas de historial automáticamente.
2.  **Plan Sanitario**: Gestión integral de vacunas y desparasitaciones con control de vencimientos.

## Próximos pasos

- Integración con facturación de Odoo.
- Notificaciones automáticas (WhatsApp/Email) para turnos y vacunas.
- Validaciones avanzadas de datos.

## Objetivo del proyecto

Más allá de lo técnico, la idea es construir algo que podría usarse en un caso real, manteniendo el código lo más claro posible.

## Estado

En desarrollo
