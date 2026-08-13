#!/usr/bin/env python3
"""Validate portable top-level Scaena Skills."""

from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
errors = []
skills = sorted(root.glob("*/SKILL.md"))
for skill in skills:
    text = skill.read_text(encoding="utf-8")
    match = re.search(r"(?m)^name:\s*(.+?)\s*$", text)
    name = match.group(1).strip("\"'") if match else None
    if name != skill.parent.name:
        errors.append(f"{skill}: invalid name")
    if not re.search(r"(?m)^description:\s*.+$", text):
        errors.append(f"{skill}: missing description")
    if "/workspaces/yeisme-agent" in text or "/home/yeisme" in text:
        errors.append(f"{skill}: contains a maintainer-specific path")
    metadata = skill.parent / "agents" / "openai.yaml"
    if not metadata.is_file():
        errors.append(f"{skill.parent}: missing agents/openai.yaml")
    elif any(field not in metadata.read_text(encoding="utf-8") for field in ("display_name:", "short_description:", "default_prompt:")):
        errors.append(f"{metadata}: incomplete metadata")
if len(skills) != 3:
    errors.append(f"expected 3 Scaena Skills, found {len(skills)}")
if errors:
    print("FAIL", *errors, sep="\n- ", file=sys.stderr)
    raise SystemExit(1)
print("PASS: validated 3 portable Scaena Skills")
