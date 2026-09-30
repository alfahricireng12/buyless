"""Domain checks for the optional helper, not tests of any host AI's reasoning."""

import copy
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("compare_offers", ROOT / "scripts" / "compare_offers.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples" / "offers.synthetic.json").read_text(encoding="utf-8"))

    def one(self, **changes):
        row = self.data["offers"][0]
        row.update(changes)
        self.data["offers"] = [row]
        return row

    def row(self):
        return helper.compare(self.data)["groups"][0]["offers"][0]

    def test_capped_coupon_and_cashback(self):
        self.one()
        result = self.row()
        self.assertEqual(result["discount"], "300000")
        self.assertEqual(result["total"], "3925000")
        self.assertEqual(result["cashback_separate"], "100000")

    def test_cheapest_complete_offer(self):
        result = helper.compare(self.data)
        complete = next(g for g in result["groups"] if g["price_class"] == "complete")
        self.assertEqual(complete["lowest_id"], "domestic-a")
        self.assertEqual([r["id"] for r in complete["offers"]], ["domestic-a", "domestic-b"])

    def test_missing_shipping_is_not_zero_or_winner(self):
        self.one(shipping=None)
        report = helper.compare(self.data)
        self.assertIsNone(report["groups"][0]["lowest_id"])
        self.assertIsNone(self.row()["total"])
        self.assertIn("shipping", self.row()["unknown_charges"])

    def test_pickup_payment_separate_from_delivery(self):
        groups = helper.compare(self.data)["groups"]
        pickup = next(g for g in groups if g["fulfillment"] == "pickup")
        self.assertEqual(pickup["price_class"], "pickup_payment")
        self.assertIsNone(pickup["offers"][0]["total"])
        self.assertIn("travel_cost", pickup["offers"][0]["unknown_charges"])

    def test_unknown_destination_is_unqualified(self):
        self.one(eligible=None)
        result = helper.compare(self.data)
        self.assertFalse(result["groups"])
        self.assertEqual(len(result["unqualified"]), 1)

    def test_wrong_variant_excluded(self):
        self.assertIn("wrong-variant", [x["id"] for x in helper.compare(self.data)["excluded"]])

    def test_unavailable_excluded(self):
        self.one(available=False)
        self.assertEqual(len(helper.compare(self.data)["excluded"]), 1)

    def test_radius_respected(self):
        self.one(fulfillment="pickup", distance_km="11")
        self.assertEqual(len(helper.compare(self.data)["excluded"]), 1)

    def test_unknown_distance_does_not_meet_radius(self):
        self.one(fulfillment="pickup")
        self.assertEqual(len(helper.compare(self.data)["unqualified"]), 1)

    def test_expired_coupon_not_applied(self):
        row = self.one()
        row["promotions"][0]["expires_at"] = self.data["checked_at"]
        self.assertEqual(self.row()["discount"], "0")

    def test_future_coupon_not_applied(self):
        row = self.one()
        row["promotions"][0]["starts_at"] = "2026-09-28T00:00:00+07:00"
        self.assertEqual(self.row()["discount"], "0")

    def test_personal_eligibility_not_inferred(self):
        row = self.one()
        row["promotions"][0]["eligibility"] = "unknown"
        self.assertEqual(self.row()["discount"], "0")

    def test_minimum_spend(self):
        self.one(item_price="2000000")
        self.assertEqual(self.row()["discount"], "0")

    def test_selects_single_best_coupon_without_stacking(self):
        row = self.one()
        extra = {"code": "FIXED", "kind": "fixed", "value": "400000", "minimum": "0", "eligibility": "confirmed", "validity_confirmed": True}
        row["promotions"].append(extra)
        result = self.row()
        self.assertEqual(result["discount"], "400000")
        self.assertEqual(result["applied_coupon"], "FIXED")

    def test_discount_does_not_exceed_item_price(self):
        row = self.one()
        row["promotions"] = [{"code": "BIG", "kind": "fixed", "value": "9000000", "minimum": "0", "eligibility": "confirmed", "validity_confirmed": True}]
        self.assertEqual(self.row()["total"], "25000")

    def test_currencies_do_not_mix(self):
        self.data["offers"] = self.data["offers"][:2]
        self.data["offers"][1]["currency"] = "USD"
        self.assertEqual(len(helper.compare(self.data)["groups"]), 2)

    def test_warranty_groups_do_not_mix(self):
        self.data["offers"] = self.data["offers"][:2]
        self.data["offers"][1]["warranty"] = "different territory"
        self.assertEqual(len(helper.compare(self.data)["groups"]), 2)

    def test_estimates_have_no_confirmed_winner(self):
        self.one(certainty="estimated")
        self.assertIsNone(helper.compare(self.data)["groups"][0]["lowest_id"])

    def test_conditional_offers_unqualified(self):
        self.one(certainty="conditional")
        self.assertFalse(helper.compare(self.data)["groups"])

    def test_exact_decimal_rounding(self):
        row = self.one(currency="USD", item_price="0.30", shipping="0.10", promotions=[])
        self.assertEqual(self.row()["total"], "0.40")

    def test_invalid_money_rejected(self):
        for invalid in (True, "NaN", "Infinity", "-1", "1000000000001", [], {}):
            with self.subTest(invalid=invalid), self.assertRaises(helper.InputError):
                helper.amount(invalid)

    def test_missing_location_rejected(self):
        self.data["location"] = {}
        with self.assertRaises(helper.InputError):
            helper.compare(self.data)

    def test_missing_timezone_rejected(self):
        self.data["checked_at"] = "2026-09-27T12:00:00"
        with self.assertRaises(helper.InputError):
            helper.compare(self.data)

    def test_unsafe_source_rejected(self):
        self.one(url="javascript:alert(1)")
        with self.assertRaises(helper.InputError):
            helper.compare(self.data)

    def test_duplicates_rejected(self):
        self.data["offers"].append(copy.deepcopy(self.data["offers"][0]))
        with self.assertRaises(helper.InputError):
            helper.compare(self.data)

    def test_numeric_boolean_not_eligibility(self):
        self.one(eligible=1)
        with self.assertRaises(helper.InputError):
            helper.compare(self.data)

    def test_markdown_escapes_table_and_html(self):
        self.one(seller="Shop | <script>\nline")
        report = helper.markdown(helper.compare(self.data))
        self.assertIn("Shop \\| &lt;script&gt; line", report)
        self.assertNotIn("<script>", report)

    def test_empty_report(self):
        self.data["offers"] = []
        self.assertIn("No offers", helper.markdown(helper.compare(self.data)))

    def test_markdown_discloses_cashback_and_breakdown(self):
        self.one()
        output = helper.markdown(helper.compare(self.data))
        self.assertIn("Cashback/future benefit, separate: IDR 100000", output)
        self.assertIn("Immediate discount: -300000", output)

    def test_cli_json(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "compare_offers.py"), str(ROOT / "examples" / "offers.synthetic.json"), "--format", "json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["offer_count"], 6)

    def test_cli_missing_file(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "compare_offers.py"), str(ROOT / "examples" / "missing.json")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("BuyLess input error", result.stderr)


if __name__ == "__main__":
    unittest.main()
