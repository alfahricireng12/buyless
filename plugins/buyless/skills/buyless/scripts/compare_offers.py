#!/usr/bin/env python3
"""Offline exact-money support for BuyLess. No network calls or external packages."""

import argparse
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


class InputError(ValueError):
    """An observation is malformed; never silently turn it into a cheap offer."""


def amount(value, label="amount", nullable=False):
    if value is None and nullable:
        return None
    if isinstance(value, bool) or value is None or not isinstance(value, (str, int, float, Decimal)):
        raise InputError(f"{label}: use a nonnegative decimal amount or null where allowed")
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        raise InputError(f"{label}: invalid decimal amount") from None
    if not result.is_finite() or not 0 <= result <= Decimal("1000000000000"):
        raise InputError(f"{label}: amount must be finite and between 0 and 1 trillion")
    return result


def text(obj, name):
    value = obj.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise InputError(f"{name}: nonempty text of at most 2000 characters is required")
    return value.strip()


def timestamp(value, label):
    if not isinstance(value, str):
        raise InputError(f"{label}: timestamp with timezone is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise InputError(f"{label}: invalid ISO 8601 timestamp") from None
    if parsed.tzinfo is None:
        raise InputError(f"{label}: timezone is required")
    return parsed


def link(value):
    if not isinstance(value, str) or len(value) > 4096 or any(c.isspace() for c in value):
        raise InputError("url: use an HTTP/HTTPS source without whitespace")
    try:
        parts = urlsplit(value)
        valid = parts.scheme in {"http", "https"} and parts.hostname and not parts.username and not parts.password
    except ValueError:
        valid = False
    if not valid:
        raise InputError("url: use an HTTP/HTTPS source without embedded credentials")
    return value


def tri_state(obj, name):
    if name not in obj or not (obj[name] is None or type(obj[name]) is bool):
        raise InputError(f"{name}: true, false, or null is required")
    return obj[name]


def round_money(value, currency):
    unit = Decimal("1") if currency in {"IDR", "JPY", "KRW"} else Decimal("0.01")
    return value.quantize(unit, rounding=ROUND_HALF_UP)


def coupon(c, subtotal, currency, at):
    if not isinstance(c, dict):
        raise InputError("promotion: expected an object")
    code = text(c, "code")
    if c.get("eligibility") not in {"confirmed", "unknown", "ineligible"}:
        raise InputError(f"{code}: invalid eligibility")
    if type(c.get("validity_confirmed")) is not bool:
        raise InputError(f"{code}: validity_confirmed must be a boolean")
    if c.get("kind") not in {"fixed", "percent"}:
        raise InputError(f"{code}: only fixed or percent item coupons are supported")
    value, minimum = amount(c.get("value"), code), amount(c.get("minimum"), code)
    if c["kind"] == "percent" and (value > 100 or "cap" not in c):
        raise InputError(f"{code}: percent must be at most 100 and cap must be explicit")
    cap = amount(c.get("cap"), code, nullable=True)
    starts = timestamp(c["starts_at"], code) if c.get("starts_at") is not None else None
    expires = timestamp(c["expires_at"], code) if c.get("expires_at") is not None else None
    if starts and expires and starts >= expires:
        raise InputError(f"{code}: invalid validity interval")
    if c.get("source_url"):
        link(c["source_url"])
    reason = None
    if c["eligibility"] != "confirmed":
        reason = "Eligibility is not confirmed."
    elif not c["validity_confirmed"]:
        reason = "Validity is not confirmed."
    elif (starts and at < starts) or (expires and at >= expires):
        reason = "Outside the validity period at the observation time."
    elif subtotal < minimum:
        reason = "Minimum item spend is not met."
    discount = value if c["kind"] == "fixed" else subtotal * value / 100
    if c["kind"] == "percent" and cap is not None:
        discount = min(discount, cap)
    return code, Decimal(0) if reason else round_money(min(subtotal, discount), currency), reason


def evaluate_offer(offer, at, radius):
    if not isinstance(offer, dict):
        raise InputError("offer: expected an object")
    result = {k: text(offer, k) for k in ("id", "product_group", "title", "seller", "currency", "condition", "warranty")}
    result["url"] = link(offer.get("url"))
    currency = result["currency"]
    if not re.fullmatch(r"[A-Z]{3}", currency):
        raise InputError("currency: use three uppercase letters")
    fulfillment = offer.get("fulfillment")
    if fulfillment not in {"delivery", "pickup"}:
        raise InputError("fulfillment: choose delivery or pickup")
    match = offer.get("match")
    if match not in {"confirmed", "possible", "rejected"}:
        raise InputError("match: choose confirmed, possible, or rejected")
    certainty = offer.get("certainty")
    if certainty not in {"observed", "estimated", "conditional"}:
        raise InputError("certainty: choose observed, estimated, or conditional")
    eligible, available = tri_state(offer, "eligible"), tri_state(offer, "available")
    subtotal = amount(offer.get("item_price"), "item_price")
    charges = {}
    for key in ("shipping", "fees", "import_charges"):
        if key not in offer:
            raise InputError(f"{key}: provide an amount or explicit null")
        charges[key] = amount(offer[key], key, nullable=True)
    if fulfillment == "pickup":
        charges["travel_cost"] = amount(offer.get("travel_cost"), "travel_cost", nullable=True)
    distance = amount(offer.get("distance_km"), "distance_km", nullable=True)
    reasons, eligibility_class = [], "candidate"
    if match == "rejected" or eligible is False or available is False:
        eligibility_class = "excluded"
        if match == "rejected":
            reasons.append("Product does not match.")
        if eligible is False:
            reasons.append("Not eligible for the selected destination or pickup.")
        if available is False:
            reasons.append("Not available at the observation time.")
    if fulfillment == "pickup" and radius is not None and distance is not None and distance > radius:
        eligibility_class = "excluded"
        reasons.append("Outside the specified pickup radius.")
    unresolved = match != "confirmed" or eligible is not True or available is not True or certainty == "conditional"
    if fulfillment == "pickup" and radius is not None and distance is None:
        unresolved = True
        reasons.append("Distance is unknown; compliance with the radius is unconfirmed.")
    if unresolved and eligibility_class != "excluded":
        eligibility_class = "unqualified"
        reasons.append("Confirm product match, availability, eligibility, and conditions before ranking.")
    promotions = offer.get("promotions", [])
    if not isinstance(promotions, list) or len(promotions) > 10:
        raise InputError("promotions: at most 10 single-item coupon objects are supported")
    applied, discount, evaluated = None, Decimal(0), []
    seen_codes = set()
    for promo in promotions:
        code, reduction, why = coupon(promo, subtotal, currency, at)
        if code in seen_codes:
            raise InputError("promotions: duplicate coupon code")
        seen_codes.add(code)
        evaluated.append({"code": code, "discount": str(reduction), "reason": why})
        if reduction > discount:
            applied, discount = code, reduction
    known = round_money(subtotal - discount + sum((x for x in charges.values() if x is not None), Decimal(0)), currency)
    unknown = [k for k, v in charges.items() if v is None]
    price_class = "complete" if not unknown else "incomplete"
    if fulfillment == "pickup" and unknown == ["travel_cost"]:
        price_class = "pickup_payment"
    if certainty == "estimated":
        price_class = "estimated_" + price_class
    notes = offer.get("notes", [])
    if not isinstance(notes, list) or not all(isinstance(n, str) and len(n) <= 2000 for n in notes):
        raise InputError("notes: use an array of short strings")
    result.update({
        "fulfillment": fulfillment, "certainty": certainty, "eligibility_class": eligibility_class,
        "price_class": price_class, "known_subtotal": str(known),
        "total": str(known) if not unknown else None, "unknown_charges": unknown,
        "discount": str(discount), "applied_coupon": applied, "coupon_checks": evaluated,
        "cashback_separate": str(amount(offer.get("cashback", "0"), "cashback")),
        "distance_km": str(distance) if distance is not None else None,
        "reasons": reasons, "notes": notes,
        "trace": [{"label": "Item price", "amount": str(subtotal)},
                  {"label": "Immediate discount", "amount": str(-discount)}] +
                 [{"label": k.replace("_", " "), "amount": str(v) if v is not None else None} for k, v in charges.items()],
    })
    return result


def compare(document):
    if not isinstance(document, dict) or type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        raise InputError("schema_version: expected integer 1")
    if type(document.get("synthetic")) is not bool:
        raise InputError("synthetic: explicit true or false is required")
    location = document.get("location")
    if not isinstance(location, dict):
        raise InputError("location: an object with a label is required")
    label = text(location, "label")
    radius = amount(location.get("radius_km"), "radius_km", nullable=True)
    if radius is not None and radius <= 0:
        raise InputError("radius_km: must be positive")
    at = timestamp(document.get("checked_at"), "checked_at")
    offers = document.get("offers")
    if not isinstance(offers, list) or len(offers) > 200:
        raise InputError("offers: provide an array of at most 200 observations")
    groups, unqualified, excluded, ids = {}, [], [], set()
    for raw in offers:
        row = evaluate_offer(raw, at, radius)
        if row["id"] in ids:
            raise InputError("offers: duplicate id")
        ids.add(row["id"])
        if row["eligibility_class"] == "excluded":
            excluded.append(row)
        elif row["eligibility_class"] == "unqualified":
            unqualified.append(row)
        else:
            key = tuple(row[k] for k in ("product_group", "condition", "warranty", "currency", "fulfillment", "price_class"))
            groups.setdefault(key, []).append(row)
    output_groups = []
    priority = {"complete": 0, "pickup_payment": 1, "estimated_complete": 2, "estimated_pickup_payment": 3, "incomplete": 4, "estimated_incomplete": 5}
    for key, rows in sorted(groups.items(), key=lambda entry: (priority.get(entry[0][5], 6), entry[0])):
        rows.sort(key=lambda row: (Decimal(row["known_subtotal"]), row["id"]))
        output_groups.append({
            "product_group": key[0], "condition": key[1], "warranty": key[2],
            "currency": key[3], "fulfillment": key[4], "price_class": key[5],
            "lowest_id": rows[0]["id"] if key[5] in {"complete", "pickup_payment"} else None,
            "offers": rows,
        })
    return {
        "schema_version": 1, "synthetic": document["synthetic"], "location": label,
        "checked_at": at.isoformat(), "groups": output_groups, "unqualified": unqualified,
        "excluded": excluded, "offer_count": len(offers),
        "notice": "Arithmetic on supplied observations only. No live search or factual verification. No global cheapest claim.",
    }


def cell(value):
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ").replace("<", "&lt;").replace(">", "&gt;").replace("[", "\\[").replace("]", "\\]")


def markdown(report):
    lines = ["# BuyLess comparison", "", "**SYNTHETIC EXAMPLE — not real offers.**" if report["synthetic"] else "**Based on supplied observations; not independently verified.**", "",
             f"Location: {cell(report['location'])}. Observed: {cell(report['checked_at'])}.", "", report["notice"], ""]
    for group in report["groups"]:
        lines += [f"## {cell(group['product_group'])} · {group['currency']} · {group['fulfillment']} · {group['price_class']}", "",
                  f"Condition: {cell(group['condition'])}. Warranty: {cell(group['warranty'])}.", "",
                  "| Seller | Known amount | Unknown charges | Immediate coupon | Source |", "|---|---:|---|---|---|"]
        for row in group["offers"]:
            url = row["url"].replace("(", "%28").replace(")", "%29").replace("<", "%3C").replace(">", "%3E")
            lines.append(f"| {cell(row['seller'])} | {group['currency']} {row['known_subtotal']} | {cell(', '.join(row['unknown_charges']) or 'None recorded')} | {cell(row['applied_coupon'] or 'None applied')} | [Source]({url}) |")
        if group["lowest_id"]:
            suffix = " (pickup payment only; travel is excluded)" if group["price_class"] == "pickup_payment" else ""
            lines += ["", f"Lowest within this observed group: {cell(group['lowest_id'])}{suffix}."]
        else:
            lines += ["", "No confirmed cheapest total in this estimated or incomplete group."]
        lines += [""]
        for row in group["offers"]:
            breakdown = "; ".join(f"{cell(part['label'])}: {cell(part['amount'] if part['amount'] is not None else 'unknown')}" for part in row["trace"])
            lines += [f"- {cell(row['seller'])}: {breakdown}. Cashback/future benefit, separate: {group['currency']} {row['cashback_separate']}."]
        lines += [""]
    for label in ("unqualified", "excluded"):
        if report[label]:
            lines += [f"## {label.capitalize()}", ""]
            lines += [f"- {cell(r['id'])}: {cell(' '.join(r['reasons']))}" for r in report[label]]
            lines += [""]
    if not report["groups"]:
        lines += ["No offers are qualified for a comparable group.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Local JSON observations (no URLs are fetched)")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args(argv)
    try:
        if args.input.stat().st_size > 2_000_000:
            raise InputError("Input exceeds the 2 MB limit")
        document = json.loads(args.input.read_text(encoding="utf-8-sig"), parse_float=Decimal)
        report = compare(document)
        print(json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else markdown(report))
        return 0
    except (InputError, OSError, ValueError) as exc:
        print(f"BuyLess input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
