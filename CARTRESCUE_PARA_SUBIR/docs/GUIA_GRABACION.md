# Guion de grabación y lista de verificación

Este documento organiza una presentación corta y clara del proyecto. El video lo prepara el integrante responsable de la grabación; por ahora no hay enlace público de video ni despliegue. El repositorio que se puede mostrar es [CARTRESCUE en GitHub](https://github.com/Incomu1/CARTRESCUE).

## Índice

1. Antes de empezar
2. Reparto de la presentación
3. Ejecución desde cero
4. Qué escenarios mostrar
5. Cierre y lista de verificación

## 1. Antes de empezar

- Usar únicamente la carpeta local `CARTRESCUE/` y los datos sintéticos que ya contiene.
- Evitar mostrar cuentas, correos, credenciales o información de una tienda real.
- Tener a mano `README.md`, `docs/DISENO_CORREGIDO_AMPLIADO.pdf`, `evidence/reproducible_run/summary.json` y `events.ndjson`.
- Si se muestra el repositorio, aclarar que el proyecto no tiene video ni despliegue público todavía.

## 2. Reparto de la presentación (hasta 18 minutos)

| Tiempo | Quién presenta | Qué conviene explicar |
|---:|---|---|
| 0:00–1:30 | Integrante 1 | El problema: recuperar carritos sin convertir el sistema en mensajería indiscriminada. Mencionar que todo es una simulación. |
| 1:30–4:00 | Integrante 1 | La comparación con KnowKeeper y la decisión del equipo: 4.30 frente a 2.75. Señalar el tradeoff: KnowKeeper aporta continuidad del conocimiento, pero exige un entorno más sensible y complejo. |
| 4:00–7:00 | Integrante 1 | Arquitectura, reglas de contacto y diagrama de secuencia. Dejar claro que los servicios externos no están implementados. |
| 7:00–10:00 | Integrante 2 | Desde una terminal limpia, mostrar versión de Python, ejecutar pruebas y lanzar la simulación con semilla. |
| 10:00–13:00 | Integrante 2 | Un caso normal: `normal_email` o `cliente_recurrente`. Mostrar decisión, acción sintética y resultado. |
| 13:00–15:30 | Integrante 2 | Dos bloqueos: `sin_consentimiento` y `limite_contactos`. Mostrar `none`, el motivo y la ausencia de `action_executed`. |
| 15:30–17:00 | Integrante 2 | Abrir `summary.json` y explicar 35% de recuperación simulada, 100% de bloqueos correctamente registrados y sus límites. |
| 17:00–18:00 | Ambos | Cerrar con limitaciones, próximas validaciones y el estado pendiente del video/despliegue. |

## 3. Ejecución desde cero

```bash
cd '/home/fedora/Documentos/Inteligencia artificial parcial/CARTRESCUE'
python3 --version
python3 -m unittest discover -s tests -v
python3 -m cartrescue --all --runs 5 --seed 20261019 --output evidence/reproducible_run
```

La semilla mantiene el mismo recorrido estocástico. El último comando vuelve a escribir evidencia local; no envía mensajes ni modifica datos externos.

## 4. Qué escenarios mostrar

- **Caso normal:** `cliente_recurrente` o `normal_email`. Relacionar la decisión con la utilidad y el resultado registrado.
- **Casos de política:** `sin_consentimiento` y `limite_contactos`. En `scenario_results.csv` deben aparecer con acción `none`; en `events.ndjson`, con su motivo.
- **Aclaración necesaria:** `synthetic_channel=True` solo indica que el simulador registró una acción. No significa que se envió un correo ni una notificación.

## 5. Cierre y lista de verificación

- [ ] La cámara muestra terminal y documentos sin datos personales ni credenciales.
- [ ] Se escucha con claridad a ambos integrantes y cada uno se presenta al iniciar su parte.
- [ ] Se enseña una ejecución desde cero, un caso normal y dos bloqueos.
- [ ] Se explican resultados y límites sin prometer desempeño real.
- [ ] Se menciona el repositorio público: `https://github.com/Incomu1/CARTRESCUE`.
- [ ] El enlace del video se agrega solo después de grabarlo y subirlo: **pendiente**.
- [ ] El enlace de despliegue se agrega solo si se hace un despliegue real: **pendiente**.
