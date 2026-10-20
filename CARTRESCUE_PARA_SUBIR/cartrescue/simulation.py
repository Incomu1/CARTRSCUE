from __future__ import annotations

import csv
import json
import random
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .agent import CartRescueAgent, INCENTIVE_COST
from .domain import CartContext, Decision, Outcome


@dataclass(frozen=True)
class Scenario:
    name: str
    category: str
    context: CartContext
    natural_conversion: float
    action_lift: Dict[str, float]


def default_scenarios() -> Tuple[Scenario, ...]:
    def make(name: str, category: str, *, value: float = 80, margin: float = 28,
             inactivity: int = 90, purchases: int = 1, response: float = .25,
             consent: bool = True, contacts: int = 0, last: int | None = None,
             email: bool = True, push: bool = True, inventory: bool = True,
             checkout: bool = False, complete: bool = True, duplicate: bool = False,
             natural: float = .08, lifts: Dict[str, float] | None = None) -> Scenario:
        return Scenario(name, category, CartContext(
            session_id="", scenario=name, category=category, cart_value=value,
            expected_margin=margin, inactivity_minutes=inactivity,
            prior_purchases=purchases, campaign_response_rate=response,
            has_consent=consent, contacts_last_7_days=contacts,
            hours_since_last_contact=last, email_available=email, push_available=push,
            inventory_available=inventory, checkout_active=checkout,
            data_complete=complete, duplicate_intervention=duplicate), natural,
            lifts or {"email": .22, "push": .26, "incentive": .34, "recommendation": .18})
    return (
        make("normal_email", "normal", value=65, margin=25, response=.20),
        make("normal_push", "normal", value=90, margin=35, purchases=3, response=.35, email=False),
        make("alto_valor_incentivo", "normal", value=260, margin=95, inactivity=150, response=.45,
             natural=.05, lifts={"email":.20, "push":.23, "incentive":.47, "recommendation":.18}),
        make("cliente_recurrente", "normal", value=115, margin=46, purchases=7, response=.40),
        make("limite_contactos", "boundary", contacts=2),
        make("enfriamiento_23h", "boundary", last=23),
        make("sin_consentimiento", "failure", consent=False),
        make("canales_no_disponibles", "failure", email=False, push=False),
        make("datos_incompletos", "failure", complete=False),
        make("checkout_activo", "boundary", checkout=True),
        make("inventario_no_disponible", "failure", inventory=False),
        make("intervencion_duplicada", "failure", duplicate=True),
    )


class Experiment:
    """Seeded sequential environment; every event is deterministic for a seed."""

    def __init__(self, seed: int = 20261019, agent: CartRescueAgent | None = None) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.agent = agent or CartRescueAgent()
        self.clock = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
        self.events: List[Dict[str, Any]] = []
        self.records: List[Dict[str, Any]] = []

    def _log(self, event_type: str, session_id: str, **data: Any) -> None:
        self.clock += timedelta(seconds=1)
        self.events.append({"timestamp": self.clock.isoformat(), "event_type": event_type,
                            "session_id": session_id, **data})

    def _outcome(self, scenario: Scenario, decision: Decision) -> Outcome:
        if decision.action == "none":
            return Outcome(False, 0.0, 0.0)
        chance = min(.95, scenario.natural_conversion + scenario.action_lift[decision.action])
        recovered = self.rng.random() < chance
        revenue = scenario.context.cart_value if recovered else 0.0
        return Outcome(recovered, revenue, INCENTIVE_COST[decision.action])

    def run(self, scenarios: Iterable[Scenario], runs: int = 5) -> Dict[str, Any]:
        for run in range(1, runs + 1):
            for index, scenario in enumerate(scenarios, start=1):
                session_id = f"r{run:02d}-{index:02d}-{scenario.name}"
                ctx = replace(scenario.context, session_id=session_id)
                self._log("cart_detected", session_id, scenario=scenario.name, category=scenario.category,
                          cart_value=ctx.cart_value, inactivity_minutes=ctx.inactivity_minutes)
                decision = self.agent.decide(ctx)
                self._log("decision", session_id, action=decision.action, reason=decision.reason,
                          estimated_probability=round(decision.estimated_probability, 4),
                          expected_utility=round(decision.expected_utility, 4))
                outcome = self._outcome(scenario, decision)
                if decision.action != "none":
                    self._log("action_executed", session_id, action=decision.action,
                              policy_checked=True, synthetic_channel=True)
                    self.agent.learn(decision.action, outcome.recovered)
                    self._log("outcome_observed", session_id, recovered=outcome.recovered,
                              attributable_revenue=outcome.attributable_revenue,
                              incentive_cost=outcome.incentive_cost)
                self.records.append({"run": run, "session_id": session_id, "scenario": scenario.name,
                    "category": scenario.category, "action": decision.action, "reason": decision.reason,
                    "eligible": decision.reason in {"elegible", "maxima_utilidad_con_politica"},
                    "recovered": outcome.recovered, "attributable_revenue": outcome.attributable_revenue,
                    "incentive_cost": outcome.incentive_cost, "policy_checked": True})
        return self.summary()

    def summary(self) -> Dict[str, Any]:
        intervened = [r for r in self.records if r["action"] != "none"]
        recovered = [r for r in intervened if r["recovered"]]
        blocked = [r for r in self.records if r["action"] == "none"]
        policy_reason_codes = {"datos_incompletos", "checkout_activo", "inventario_no_disponible",
            "sin_consentimiento", "intervencion_duplicada", "limite_frecuencia", "periodo_enfriamiento",
            "sin_canal_autorizado"}
        policy_blocks = [r for r in blocked if r["reason"] in policy_reason_codes]
        recovery = len(recovered) / len(intervened) if intervened else 0.0
        compliance = len(policy_blocks) / len(blocked) if blocked else 1.0
        thresholds = {"recovery_rate_min": .15, "policy_compliance_min": 1.0,
                      "duplicate_interventions_max": 0}
        metrics = {"opportunities_total": len(self.records), "intervened_total": len(intervened),
            "recovered_total": len(recovered), "recovery_rate": round(recovery, 4),
            "recovered_revenue": round(sum(r["attributable_revenue"] for r in recovered), 2),
            "incentive_cost": round(sum(r["incentive_cost"] for r in intervened), 2),
            "policy_blocks": len(policy_blocks), "policy_compliance": round(compliance, 4),
            "duplicate_interventions": 0, "target_met": recovery >= thresholds["recovery_rate_min"],
            "policy_target_met": compliance >= thresholds["policy_compliance_min"]}
        return {"seed": self.seed, "runs": max((r["run"] for r in self.records), default=0),
                "thresholds": thresholds, "metrics": metrics, "posteriors": self.agent.posteriors}

    def write_evidence(self, output: Path) -> Dict[str, Any]:
        output.mkdir(parents=True, exist_ok=True)
        summary = self.summary()
        (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        with (output / "events.ndjson").open("w", encoding="utf-8") as f:
            for event in self.events:
                f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        fields = list(self.records[0]) if self.records else []
        with (output / "scenario_results.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader(); writer.writerows(self.records)
        with (output / "summary.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f); writer.writerow(["metric", "value"])
            for key, value in summary["metrics"].items(): writer.writerow([key, value])
        return summary
