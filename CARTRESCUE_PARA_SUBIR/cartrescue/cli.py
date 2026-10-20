from __future__ import annotations

import argparse
from pathlib import Path

from .simulation import Experiment, default_scenarios


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulación reproducible de CARTRESCUE-AGENT")
    parser.add_argument("--all", action="store_true", help="ejecuta el catálogo de escenarios")
    parser.add_argument("--runs", type=int, default=5, help="repeticiones por escenario (mínimo recomendado: 5)")
    parser.add_argument("--seed", type=int, default=20261019, help="semilla del entorno estocástico")
    parser.add_argument("--output", type=Path, default=Path("evidence/latest"), help="directorio de evidencia")
    args = parser.parse_args()
    if not args.all:
        parser.error("use --all para ejecutar el catálogo de escenarios")
    if args.runs < 5:
        parser.error("--runs debe ser >= 5 para cumplir el protocolo de evaluación")
    experiment = Experiment(seed=args.seed)
    experiment.run(default_scenarios(), runs=args.runs)
    summary = experiment.write_evidence(args.output)
    metrics = summary["metrics"]
    print(f"seed={summary['seed']} scenarios={len(default_scenarios())} runs={summary['runs']}")
    print(f"recovery_rate={metrics['recovery_rate']:.2%} target>=15%: {metrics['target_met']}")
    print(f"policy_compliance={metrics['policy_compliance']:.2%} target=100%: {metrics['policy_target_met']}")
    print(f"evidence={args.output}")
    return 0 if metrics["target_met"] and metrics["policy_target_met"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
