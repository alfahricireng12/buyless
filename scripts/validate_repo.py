#!/usr/bin/env python3
"""Dependency-free packaging checks; not a substitute for behavioral evaluation."""

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate():
    errors = []
    skill = ROOT / "SKILL.md"
    source = skill.read_text(encoding="utf-8-sig")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", source, re.S)
    if not frontmatter:
        errors.append("SKILL.md needs YAML frontmatter")
    else:
        header = frontmatter.group(1)
        name = re.search(r"^name: ([a-z0-9-]+)$", header, re.M)
        description = re.search(r"^description: (.+)$", header, re.M)
        if not name or name.group(1) != ROOT.name:
            errors.append("Skill name must match its directory")
        if not description or not 1 <= len(description.group(1)) <= 1024:
            errors.append("Skill description is missing or too long")
    if len(source.splitlines()) > 500:
        errors.append("Move detailed guidance out of the skill entrypoint")
    files = [p for p in ROOT.rglob("*") if p.is_file() and not any(part in {".git", "__pycache__"} for part in p.relative_to(ROOT).parts)]
    checked = 0
    for file in files:
        if file.suffix == ".md":
            checked += 1
            content = file.read_text(encoding="utf-8-sig")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if target.startswith(("http:", "https:", "#", "mailto:")):
                    continue
                relative = target.split("#")[0]
                resolved = (file.parent / relative).resolve()
                if not resolved.is_relative_to(ROOT.resolve()) or not resolved.exists():
                    errors.append(f"{file.relative_to(ROOT)}: missing or external local link {target}")
        elif file.suffix == ".json":
            try:
                json.loads(file.read_text(encoding="utf-8-sig"))
            except ValueError as exc:
                errors.append(f"{file.relative_to(ROOT)}: {exc}")
    for required in ("LICENSE", "agents/openai.yaml", "scripts/compare_offers.py", "references/offer-format.md",
                     "scripts/audit_research.py", "references/research-format.md",
                     "references/search-protocol.md", "references/authenticity.md", "references/international.md",
                     "plugins/buyless/plugin.json", "plugins/buyless/.codex-plugin/plugin.json",
                     ".agents/plugins/marketplace.json", "scripts/build_plugin.py",
                     "assets/buyless-logo.png", "assets/buyless-icon.png"):
        if not (ROOT / required).is_file():
            errors.append(f"Missing {required}")

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8-sig"))
    portable = json.loads((ROOT / "plugins/buyless/plugin.json").read_text(encoding="utf-8-sig"))
    compatibility = json.loads((ROOT / "plugins/buyless/.codex-plugin/plugin.json").read_text(encoding="utf-8-sig"))
    declared = re.search(r'^  version: "([^"]+)"$', source, re.M)
    versions = {package.get("version"), portable.get("version"), compatibility.get("version"),
                declared.group(1) if declared else None}
    if len(versions) != 1:
        errors.append(f"Version mismatch across skill, package and plugin manifests: {sorted(str(v) for v in versions)}")

    plugin_skill = ROOT / "plugins" / "buyless" / "skills" / "buyless"
    sync_pairs = [(ROOT / "SKILL.md", plugin_skill / "SKILL.md"),
                  (ROOT / "LICENSE", plugin_skill / "LICENSE"),
                  (ROOT / "LICENSE", ROOT / "plugins/buyless/LICENSE")]
    for directory in ("agents", "references", "examples"):
        for original in (ROOT / directory).rglob("*"):
            if original.is_file() and "__pycache__" not in original.parts:
                sync_pairs.append((original, plugin_skill / original.relative_to(ROOT)))
    for helper in ("compare_offers.py", "audit_research.py"):
        sync_pairs.append((ROOT / "scripts" / helper, plugin_skill / "scripts" / helper))
    for brand_asset in ("buyless-logo.png", "buyless-icon.png"):
        sync_pairs.append((ROOT / "assets" / brand_asset,
                           plugin_skill / "assets" / brand_asset))
        sync_pairs.append((ROOT / "assets" / brand_asset,
                           ROOT / "plugins/buyless/assets" / brand_asset))
    for original, bundled in sync_pairs:
        if not bundled.is_file() or original.read_bytes() != bundled.read_bytes():
            errors.append(f"Plugin bundle is not synchronized: {bundled.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Skill package valid: {checked} Markdown files, local links, JSON syntax, and required resources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate())
