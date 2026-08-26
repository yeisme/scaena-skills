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
expected_names = {
    "scaena-production-operator",
    "scaena-storyboard-breakdown",
    "scaena-subject-asset-readiness",
    "scaena-video-transfer-orchestrator",
    "scaena-local-video-operator",
}
actual_names = {skill.parent.name for skill in skills}
if actual_names != expected_names:
    errors.append(
        "Scaena Skill inventory mismatch: "
        f"missing={sorted(expected_names - actual_names)} "
        f"unexpected={sorted(actual_names - expected_names)}"
    )

operator_dir = root / "scaena-production-operator"
operator_text = (operator_dir / "SKILL.md").read_text(encoding="utf-8")
refinement_ref = operator_dir / "references" / "episode-refinement-loop.md"
if not refinement_ref.is_file():
    errors.append(f"{refinement_ref}: missing episode refinement contract")
else:
    refinement_text = refinement_ref.read_text(encoding="utf-8")
    for required in (
        "scaena video episode-preview",
        "scaena edit timeline",
        "scaena edit select",
        "enhance run",
        "不支持 `--dry-run`",
    ):
        if required not in refinement_text:
            errors.append(f"{refinement_ref}: missing {required}")
if (
    "scaena asset draw plan" not in operator_text
    or "one bounded owner-specific repair" not in operator_text
):
    errors.append(f"{operator_dir / 'SKILL.md'}: incomplete draw/refinement workflow")
if "export package --dry-run" in operator_text:
    errors.append(f"{operator_dir / 'SKILL.md'}: uses unsupported export --dry-run flag")

readiness_dir = root / "scaena-subject-asset-readiness"
readiness_text = (readiness_dir / "SKILL.md").read_text(encoding="utf-8")
draw_ref = readiness_dir / "references" / "candidate-draw-workflow.md"
if not draw_ref.is_file():
    errors.append(f"{draw_ref}: missing candidate draw contract")
else:
    draw_text = draw_ref.read_text(encoding="utf-8")
    for required in (
        "scaena asset draw plan",
        "scaena asset draw record",
        "scaena asset draw select",
        "scaena asset draw freeze",
        "openai/gpt-5.4-image-2",
        "默认 session 上限为 5",
    ):
        if required not in draw_text:
            errors.append(f"{draw_ref}: missing {required}")
if "human-only" not in readiness_text or "candidate-draw-workflow.md" not in readiness_text:
    errors.append(f"{readiness_dir / 'SKILL.md'}: incomplete human draw gate")
if errors:
    print("FAIL", *errors, sep="\n- ", file=sys.stderr)
    raise SystemExit(1)
print(f"PASS: validated {len(skills)} portable Scaena Skills")
