import re
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT_DIR / ".agents" / "skills"


class AIDocsValidationTestCase(unittest.TestCase):
    def test_ai_first_entrypoints_exist(self) -> None:
        required_paths = [
            ROOT_DIR / "AGENTS.md",
            ROOT_DIR / ".agents" / "ARCHITECTURE.md",
            ROOT_DIR / ".agents" / "RULES.md",
            ROOT_DIR / ".agents" / "REPO_RULES.md",
            ROOT_DIR / ".agents" / "SKILLS.md",
            ROOT_DIR / ".cursor" / "rules" / "00-project.mdc",
            ROOT_DIR / ".github" / "copilot-instructions.md",
            ROOT_DIR / "skills" / "README.md",
        ]

        for path in required_paths:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"{path} should exist")

    def test_skill_index_lists_every_skill_directory(self) -> None:
        index_text = (ROOT_DIR / ".agents" / "SKILLS.md").read_text(
            encoding="utf-8"
        )
        skill_names = sorted(path.name for path in SKILLS_DIR.iterdir() if path.is_dir())

        self.assertGreater(skill_names, [])
        for skill_name in skill_names:
            with self.subTest(skill=skill_name):
                self.assertIn(f"`{skill_name}`", index_text)

    def test_skill_frontmatter_is_valid(self) -> None:
        for skill_path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
            with self.subTest(skill=skill_path.parent.name):
                metadata = self._read_frontmatter(skill_path)

                self.assertEqual(metadata.get("name"), skill_path.parent.name)
                self.assertRegex(metadata["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
                self.assertLessEqual(len(metadata["name"]), 64)
                self.assertIn("description", metadata)
                self.assertTrue(metadata["description"].strip())
                self.assertLessEqual(len(metadata["description"]), 1024)

    def _read_frontmatter(self, path: Path) -> dict[str, str]:
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), f"{path} must start with frontmatter")

        match = re.search(r"\n---\n", text[4:])
        self.assertIsNotNone(match, f"{path} must close frontmatter")
        end = 4 + match.start()

        metadata: dict[str, str] = {}
        for line in text[4:end].splitlines():
            if not line.strip() or line.startswith(" "):
                continue
            key, _, value = line.partition(":")
            if key and value:
                metadata[key.strip()] = value.strip()
        return metadata


if __name__ == "__main__":
    unittest.main()
