#!/usr/bin/env python3
"""Synchronize the standalone BuyLess skill into the portable plugin bundle."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "plugins" / "buyless" / "skills" / "buyless"
FILES = ("SKILL.md", "LICENSE")
DIRECTORIES = ("agents", "references", "examples")
HELPERS = ("compare_offers.py", "audit_research.py")
BRAND_ASSETS = ("buyless-logo.png", "buyless-icon.png")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "LICENSE", ROOT / "plugins" / "buyless" / "LICENSE")
    plugin_assets = ROOT / "plugins" / "buyless" / "assets"
    skill_assets = DEST / "assets"
    plugin_assets.mkdir(parents=True, exist_ok=True)
    skill_assets.mkdir(parents=True, exist_ok=True)
    for name in BRAND_ASSETS:
        shutil.copy2(ROOT / "assets" / name, plugin_assets / name)
        shutil.copy2(ROOT / "assets" / name, skill_assets / name)
    for name in FILES:
        shutil.copy2(ROOT / name, DEST / name)
    for name in DIRECTORIES:
        shutil.copytree(ROOT / name, DEST / name, dirs_exist_ok=True)
    helper_dest = DEST / "scripts"
    helper_dest.mkdir(parents=True, exist_ok=True)
    for name in HELPERS:
        shutil.copy2(ROOT / "scripts" / name, helper_dest / name)
    print(f"BuyLess plugin skill synchronized: {DEST}")


if __name__ == "__main__":
    main()
