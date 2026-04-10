# Sistema de Gestión para Veterinaria - Odoo 17

Este proyecto nace como una práctica personal para seguir aprendiendo desarrollo en Odoo, pero con la idea de resolver un caso real: la gestión básica de una veterinaria.

La idea principal es evitar procesos manuales o en papel y llevar todo a un sistema simple, ordenado y escalable.

## ¿Qué incluye por ahora?

Actualmente el módulo está enfocado en la base del sistema:

- Gestión de mascotas
- Relación entre mascotas y sus dueños
- Turnos para consultas veterinarias
- Asociación de turnos con veterinarios

## Modelo de datos

Se intentó mantener lo más simple posible reutilizando modelos propios de Odoo:

- Los dueños se manejan como contactos (`res.partner`)
- Los veterinarios como usuarios (`res.users`)
- Las mascotas están vinculadas a sus dueños
- Los turnos conectan mascotas con veterinarios en una fecha determinada

Esto permite no duplicar información y aprovechar la estructura que ya trae Odoo.

## En qué estoy trabajando ahora

El foco actual está en los turnos, especialmente en:

- Evitar la superposición de horarios
- Mejorar la gestión de agenda

## Próximos pasos

Algunas ideas para seguir avanzando:

- Historial clínico de cada mascota
- Integración con facturación
- Mejoras en la visualización de turnos (tipo agenda)
- Validaciones adicionales en los datos
- Integración con WhatsApp

## Objetivo del proyecto

Más allá de lo técnico, la idea es construir algo que podría usarse en un caso real, manteniendo el código lo más claro posible.

## Estado

En desarrollo
