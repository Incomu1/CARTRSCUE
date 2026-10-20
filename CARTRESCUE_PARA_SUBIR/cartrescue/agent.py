from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Tuple

from .domain import CartContext, Decision

ACTIONS = ("email", "push", "incentive", "recommendation")
INCENTIVE_COST = {"email": 0.02, "push": 0.01, "incentive": 8.00, "recommendation": 0.05}


@dataclass
class CartRescueAgent:
    """Learning, utility-based agent with explicit contact-policy gates.

    Learning is a Beta-Bernoulli posterior per action. It is deliberately simple,
    auditable and appropriate for a synthetic coursework simulation; it is not a
    production propensity model.
    """

    posteriors: Dict[str, list[float]] = field(
        default_factory=lambda: {action: [3.0, 7.0] for action in ACTIONS}
    )
    max_contacts_7_days: int = 2
    cooldown_hours: int = 24

    def eligibility(self, ctx: CartContext) -> Tuple[bool, str]:
        if not ctx.data_complete:
            return False, "datos_incompletos"
        if ctx.checkout_active:
            return False, "checkout_activo"
        if not ctx.inventory_available:
            return False, "inventario_no_disponible"
        if not ctx.has_consent:
            return False, "sin_consentimiento"
        if ctx.duplicate_intervention:
            return False, "intervencion_duplicada"
        if ctx.contacts_last_7_days >= self.max_contacts_7_days:
            return False, "limite_frecuencia"
        if ctx.hours_since_last_contact is not None and ctx.hours_since_last_contact < self.cooldown_hours:
            return False, "periodo_enfriamiento"
        if not (ctx.email_available or ctx.push_available):
            return False, "sin_canal_autorizado"
        return True, "elegible"

    @staticmethod
    def _segment_adjustment(ctx: CartContext) -> float:
        # Observable proxy only: the user's private motives remain unobserved.
        inactivity = min(ctx.inactivity_minutes / 180.0, 1.0)
        value = min(ctx.cart_value / 300.0, 1.0)
        history = min(ctx.prior_purchases / 8.0, 1.0)
        return -0.08 + 0.16 * inactivity + 0.08 * value + 0.12 * history + 0.12 * ctx.campaign_response_rate

    def probability(self, action: str, ctx: CartContext) -> float:
        alpha, beta = self.posteriors[action]
        posterior_mean = alpha / (alpha + beta)
        action_adjustment = {"email": 0.00, "push": 0.02, "incentive": 0.10, "recommendation": 0.04}[action]
        return max(0.01, min(0.95, posterior_mean + self._segment_adjustment(ctx) + action_adjustment))

    def decide(self, ctx: CartContext) -> Decision:
        eligible, reason = self.eligibility(ctx)
        if not eligible:
            return Decision("none", reason, 0.0, 0.0)
        candidates: Iterable[str] = ACTIONS
        if not ctx.email_available:
            candidates = tuple(a for a in candidates if a != "email")
        if not ctx.push_available:
            candidates = tuple(a for a in candidates if a != "push")
        # Incentives are not considered for low-margin carts.
        if ctx.expected_margin < 12:
            candidates = tuple(a for a in candidates if a != "incentive")
        scored = []
        for action in candidates:
            p = self.probability(action, ctx)
            fatigue_cost = 0.12 * ctx.contacts_last_7_days
            utility = p * ctx.expected_margin - INCENTIVE_COST[action] - fatigue_cost
            scored.append((utility, action, p))
        utility, action, probability = max(scored)
        if utility <= 0:
            return Decision("none", "utilidad_no_positiva", probability, utility)
        return Decision(action, "maxima_utilidad_con_politica", probability, utility)

    def learn(self, action: str, recovered: bool) -> None:
        if action not in self.posteriors:
            return
        self.posteriors[action][0 if recovered else 1] += 1.0
