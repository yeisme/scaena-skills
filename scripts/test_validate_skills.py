"""Validate referenced contracts without forcing duplicated English prose."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class ValidatorTests(unittest.TestCase):
    def test_delegation_passes_and_missing_contracts_fail(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(source / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
            for skill in source.glob("*/SKILL.md"):
                shutil.copytree(skill.parent, root / skill.parent.name)
            def validate():
                return subprocess.run(["python3", "scripts/validate_skills.py"], cwd=root, capture_output=True).returncode
            self.assertEqual(validate(), 0)
            workflow = root / "scaena-production-operator/references/workflow.md"
            text = workflow.read_text()
            workflow.write_text(text.replace("scaena asset draw plan", "missing-command"))
            self.assertNotEqual(validate(), 0)
            workflow.write_text(text)
            operator = root / "scaena-production-operator/SKILL.md"
            operator.write_text(operator.read_text().replace("references/workflow.md", "references/missing.md"))
            self.assertNotEqual(validate(), 0)


if __name__ == "__main__":
    unittest.main()
