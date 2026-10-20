import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from cartrescue.agent import CartRescueAgent
from cartrescue.simulation import Experiment, default_scenarios


class CartRescueTests(unittest.TestCase):
    def test_policy_blocks_unconsented_contact(self):
        scenario = next(s for s in default_scenarios() if s.name == "sin_consentimiento")
        decision = CartRescueAgent().decide(scenario.context)
        self.assertEqual((decision.action, decision.reason), ("none", "sin_consentimiento"))

    def test_policy_blocks_frequency_boundary(self):
        scenario = next(s for s in default_scenarios() if s.name == "limite_contactos")
        self.assertEqual(CartRescueAgent().decide(scenario.context).reason, "limite_frecuencia")

    def test_seeded_run_is_reproducible(self):
        def execute():
            e = Experiment(seed=20261019); e.run(default_scenarios(), runs=5); return e.summary()["metrics"]
        self.assertEqual(execute(), execute())

    def test_evidence_has_timestamped_events_and_thresholds(self):
        e = Experiment(seed=20261019); e.run(default_scenarios(), runs=5)
        with tempfile.TemporaryDirectory() as tmp:
            summary = e.write_evidence(Path(tmp))
            self.assertTrue((Path(tmp) / "events.ndjson").exists())
            self.assertEqual(len(e.records), 60)  # 12 scenarios x 5 runs
            self.assertGreaterEqual(summary["metrics"]["recovery_rate"], .15)
            self.assertEqual(summary["metrics"]["policy_compliance"], 1.0)


if __name__ == "__main__":
    unittest.main()
