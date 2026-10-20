from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CartContext:
    """Synthetic, non-identifying signals available to the agent at a decision point."""

    session_id: str
    scenario: str
    category: str
    cart_value: float
    expected_margin: float
    inactivity_minutes: int
    prior_purchases: int
    campaign_response_rate: float
    has_consent: bool
    contacts_last_7_days: int
    hours_since_last_contact: Optional[int]
    email_available: bool
    push_available: bool
    inventory_available: bool
    checkout_active: bool
    data_complete: bool
    duplicate_intervention: bool = False


@dataclass(frozen=True)
class Decision:
    action: str
    reason: str
    estimated_probability: float
    expected_utility: float


@dataclass(frozen=True)
class Outcome:
    recovered: bool
    attributable_revenue: float
    incentive_cost: float
