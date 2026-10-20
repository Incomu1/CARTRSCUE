# CARTRESCUE-AGENT

CARTRESCUE-AGENT es una simulación reproducible de un agente que intenta recuperar carritos abandonados sin usar datos personales reales. La idea es sencilla: antes de pensar en una oferta o un recordatorio, el agente revisa si puede intervenir; después compara opciones según su utilidad esperada.

Repositorio público: [github.com/Incomu1/CARTRESCUE](https://github.com/Incomu1/CARTRESCUE).

## Cómo revisarlo rápido

```bash
python3 -m unittest discover -s tests -v
python3 -m cartrescue --all --runs 5 --seed 20261019 --output evidence/reproducible_run
```

El primer comando revisa las reglas básicas. El segundo vuelve a generar la evidencia con la misma semilla: `events.ndjson`, `scenario_results.csv`, `summary.csv` y `summary.json`.

## Qué muestra la corrida de referencia

Se usan 12 escenarios —normales, de frontera y de fallo— con 5 repeticiones cada uno. Son 60 oportunidades sintéticas, no sesiones de clientes reales.

| Medida | Resultado de referencia | Criterio |
|---|---:|---:|
| Recuperación atribuible | 35% (7 de 20 intervenciones) | >= 15% en la simulación |
| Bloqueos de política con motivo válido | 100% (40 de 40) | 100% |
| Intervenciones duplicadas | 0 | 0 |

Estos números sirven para revisar el comportamiento del simulador. No prueban que una campaña real vaya a obtener el mismo resultado.

## Cómo toma decisiones

- **Aprende de resultados previos:** guarda una posterior Beta-Bernoulli por tipo de acción.
- **Compara utilidad:** combina probabilidad estimada, margen, costo y frecuencia de contacto.
- **Respeta límites antes de actuar:** consentimiento, frecuencia máxima, período de enfriamiento, canal, inventario, checkout, datos completos y no duplicación.
- **No contacta a nadie:** `email` y `push` son acciones simuladas; no hay integración con servicios externos.

## Archivos principales

- `cartrescue/`: dominio, agente, simulación y CLI; solo usa la biblioteca estándar de Python.
- `tests/`: pruebas de políticas, reproducibilidad y evidencia.
- `evidence/reproducible_run/`: resultados que se citan en el informe.
- `docs/DISENO_CORREGIDO_AMPLIADO.*`: informe, comparación con KnowKeeper y exportaciones DOCX/PDF.
- `docs/diagrama_secuencia_cartrescue.mmd`: diagrama Mermaid editable.
- `docs/GUIA_GRABACION.md`: plan de grabación para los dos integrantes.
- `docs/BITACORA_USO_IA.md`: registro transparente del uso de IA y de lo que todavía requiere revisión humana.

## Reproducibilidad y límites

La versión probada localmente fue Python 3.14.4 y no hay dependencias de runtime fuera de la biblioteca estándar. La semilla hace repetible el azar del experimento, pero no reemplaza una prueba con usuarios reales, consentimiento verificable, atribución acordada y revisión humana.

## Enlaces públicos

- Repositorio: [https://github.com/Incomu1/CARTRESCUE](https://github.com/Incomu1/CARTRESCUE)
- Video: **pendiente de que el integrante responsable lo grabe y lo publique**.
- Despliegue: **pendiente; no se ha implementado un despliegue público**.
