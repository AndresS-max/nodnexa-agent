# SOP Interno — Procedimiento de Soporte y Operaciones de Nodnexa

> Documento interno para colaboradores de Nodnexa
> Versión 1.2 — julio 2026
> Responsable: Dirección de Operaciones

## 1. Canales y horarios de soporte

- **Correo:** soporte@nodnexa.com (canal oficial, deja registro)
- **WhatsApp de soporte:** solo para clientes con plan de mantenimiento activo
- **Horario de atención:** lunes a viernes, 9:00–18:00 (GMT-5)
- **SLA de primera respuesta:** 24 horas hábiles (clientes con Mantenimiento Pro), 48 horas hábiles (Mantenimiento Básico y garantías vigentes)

## 2. Clasificación de tickets

| Prioridad | Definición | Tiempo objetivo de resolución |
|---|---|---|
| P1 — Crítico | Automatización caída que detiene la operación del cliente | 8 horas hábiles |
| P2 — Alto | Falla parcial: el flujo corre pero con errores en algunos casos | 2 días hábiles |
| P3 — Medio | Ajuste menor o comportamiento inesperado sin impacto operativo | 5 días hábiles |
| P4 — Bajo | Consulta, duda de uso o solicitud de mejora | 5 días hábiles (respuesta), cotización si aplica |

## 3. Flujo de atención de un ticket

1. **Registro:** todo reporte (correo o WhatsApp) se registra en el tablero de soporte con: cliente, automatización afectada, prioridad, descripción y capturas.
2. **Diagnóstico:** revisar los logs de ejecución en n8n y el historial de errores. Determinar si la causa es (a) desarrollo propio, (b) cambio en API externa, o (c) mal uso del cliente.
3. **Resolución según causa:**
   - (a) Desarrollo propio → corrección sin costo, cualquier cliente en garantía o mantenimiento.
   - (b) API externa → sin costo con mantenimiento activo; sin plan, enviar cotización de ajuste puntual antes de intervenir.
   - (c) Mal uso → guiar al cliente con el tutorial; si reincide, ofrecer sesión de re-capacitación (USD 30).
4. **Comunicación:** informar al cliente el diagnóstico y el tiempo estimado ANTES de intervenir. Nunca dejar un ticket sin respuesta más de un día hábil.
5. **Cierre:** confirmar con el cliente que el flujo opera con normalidad, documentar la causa raíz y la solución en la ficha del cliente.

## 4. Escalamiento

- Si un P1 no se resuelve en 8 horas hábiles, escala automáticamente al líder técnico.
- Si un cliente reporta el mismo fallo 3 veces en 30 días, se agenda una revisión integral del proyecto sin costo (auditoría interna de calidad).

## 5. Política de cambios de alcance

Toda solicitud que agregue funcionalidad nueva (no prevista en la propuesta original) se maneja así:

1. Registrar la solicitud como "mejora".
2. Si el cliente tiene mantenimiento con horas disponibles y la mejora toma ≤ horas restantes del mes, se ejecuta descontando esas horas.
3. En caso contrario, se envía cotización formal (tarifa de consultoría: USD 45/hora o precio cerrado).
4. Nunca ejecutar cambios de alcance sin aprobación escrita del cliente.

## 6. Entrega de proyectos (checklist obligatorio)

- [ ] Workflows probados con datos reales del cliente (mínimo 10 ejecuciones limpias consecutivas)
- [ ] Manejo de errores y notificación de fallos configurados
- [ ] Credenciales entregadas al cliente en su propio vault/cuenta (Nodnexa no retiene credenciales de producción)
- [ ] Documentación del flujo entregada (diagrama + descripción por paso)
- [ ] Video tutorial grabado y enviado
- [ ] Sesión de capacitación en vivo realizada
- [ ] Inicio del período de garantía registrado en la ficha del cliente

## 7. Datos y confidencialidad

- Los datos de clientes (documentos, bases, credenciales) se usan exclusivamente para el proyecto contratado.
- Prohibido reutilizar datos de un cliente en otro proyecto o en material de marketing sin autorización escrita.
- Al cierre de un contrato, se eliminan las copias locales de datos del cliente en un plazo máximo de 15 días.
