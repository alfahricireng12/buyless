#!/usr/bin/env python3
"""Offline checks of supplied research records. Never authenticates goods or sources."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

FAMILIES = ("nearby", "domestic_marketplaces", "domestic_retailers",
            "international", "promotions", "manufacturer")
AUTHORITIES = {
    "product_identity": {"manufacturer"},
    "seller_authorization": {"manufacturer"},
    "warranty": {"manufacturer", "platform", "seller"},
    "returns": {"platform", "seller"},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and 0 < len(value.strip()) <= 4000


def stamp(value):
    require(isinstance(value, str), "Timestamp must be text")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.utcoffset() is not None, "Timestamp needs a timezone")
    return result


def url(value):
    require(nonempty(value), "Source URL is required")
    parsed = urlsplit(value)
    require(parsed.scheme in {"http", "https"} and parsed.hostname
            and not parsed.username and not parsed.password
            and not any(c.isspace() for c in value), "Invalid source URL")


def rows(value, label, limit=500):
    require(isinstance(value, list) and len(value) <= limit, f"Invalid {label} list")
    require(all(isinstance(row, dict) for row in value), f"Invalid {label} row")
    return value


def audit(data):
    require(isinstance(data, dict), "Research must be an object")
    require(type(data.get("schema_version")) is int and data["schema_version"] == 1,
            "Unsupported schema_version")
    require(type(data.get("synthetic")) is bool, "synthetic must be boolean")
    require(nonempty(data.get("product")) and nonempty(data.get("location")),
            "Product and location are required")
    checked = stamp(data.get("checked_at"))
    require(data.get("stop_reason") in {"saturation", "budget", "access_exhausted", "user_stopped"},
            "Invalid stop_reason")
    families = data.get("families")
    require(isinstance(families, dict) and set(families) == set(FAMILIES),
            "Declare every source family exactly once")
    gaps = []
    for family, setting in families.items():
        require(isinstance(setting, dict) and setting.get("scope") in {"applicable", "not_applicable"},
                f"Invalid scope for {family}")
        if setting["scope"] == "not_applicable":
            require(nonempty(setting.get("reason")), f"Explain exclusion of {family}")
    attempts = rows(data.get("attempts"), "attempts")
    seen_attempts = set()
    counts = {family: {"checked": 0, "blocked": 0, "lead_only": 0} for family in FAMILIES}
    for row in attempts:
        family, state = row.get("family"), row.get("status")
        require(family in FAMILIES and state in {"checked", "blocked", "lead_only"}, "Invalid attempt")
        require(families[family]["scope"] == "applicable", "Attempt in excluded family")
        url(row.get("url"))
        require(stamp(row.get("checked_at")) <= checked, "Attempt is after report time")
        require(nonempty(row.get("outcome")), "Attempt outcome required")
        # Supplied stable source keys collapse mirrors/tracking URLs; host must resolve ownership.
        require(nonempty(row.get("source_key")), "source_key required")
        key = (family, row["source_key"])
        require(key not in seen_attempts, "Duplicate source in family; consolidate attempts")
        seen_attempts.add(key)
        counts[family][state] += 1
    for family in FAMILIES:
        if families[family]["scope"] == "applicable" and not counts[family]["checked"]:
            gaps.append(f"{family}: no directly checked source")

    candidates = rows(data.get("candidates"), "candidates", 200)
    results, seen_ids = [], set()
    for candidate in candidates:
        for field in ("id", "product_key", "seller_key"):
            require(nonempty(candidate.get(field)), f"Candidate {field} required")
        require(candidate["id"] not in seen_ids, "Duplicate candidate id")
        seen_ids.add(candidate["id"])
        evidence = rows(candidate.get("evidence"), "evidence", 100)
        supported, conflicts, seen_evidence = set(), [], set()
        for item in evidence:
            claim = item.get("claim")
            require(claim in AUTHORITIES, "Unknown claim")
            require(nonempty(item.get("id")) and item["id"] not in seen_evidence,
                    "Evidence ids must be unique per candidate")
            seen_evidence.add(item["id"])
            url(item.get("url"))
            require(stamp(item.get("checked_at")) <= checked, "Evidence is after report time")
            require(nonempty(item.get("observation")), "Evidence observation required")
            require(item.get("authority") in {"manufacturer", "platform", "seller", "independent", "unknown"},
                    "Invalid authority")
            require(item.get("finding") in {"supports", "contradicts", "unknown"}, "Invalid finding")
            require(item.get("currency") in {"current", "stale", "unknown"}, "Invalid evidence currency")
            for field in ("product_key", "seller_key"):
                require(nonempty(item.get(field)), f"Evidence {field} required")
            exact = all(item[k] == candidate[k] for k in ("product_key", "seller_key"))
            if item["finding"] == "contradicts" and exact:
                conflicts.append(item["id"])
            if (exact and item["finding"] == "supports" and item["currency"] == "current"
                    and item["authority"] in AUTHORITIES[claim]):
                supported.add(claim)
        missing = sorted(set(AUTHORITIES) - supported)
        status = ("unresolved_conflict" if conflicts else
                  "insufficient_evidence" if missing else "documented_checks")
        results.append({"id": candidate["id"], "status": status,
                        "missing_claims": missing, "conflicting_evidence": conflicts})
    return {
        "synthetic": data["synthetic"], "location": data["location"],
        "stop_reason": data["stop_reason"], "families": families,
        "coverage": counts, "coverage_gaps": gaps,
        "candidates": results,
        "documented_candidate_ids": [r["id"] for r in results if r["status"] == "documented_checks"],
        "notice": "Record audit only. Supplied authorities, observations and scope are not verified. "
                  "No authenticity guarantee, exhaustive search claim or price recommendation is produced.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        require(args.input.stat().st_size <= 2_000_000, "Input exceeds 2 MB")
        result = audit(json.loads(args.input.read_text(encoding="utf-8-sig")))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, TypeError, OverflowError, RecursionError) as exc:
        print(f"Invalid research: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
