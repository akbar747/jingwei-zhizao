"""发布配置契约测试。

这些测试防止版本号、资产名称和安装策略在各文件中漂移。
"""

from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseConfigurationTests(unittest.TestCase):
    def test_pyproject_declares_packaging_dependency(self):
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        version = data["project"]["version"]
        package_dependencies = data["project"]["optional-dependencies"]["package"]

        self.assertEqual(version, "0.1.3")
        self.assertIn("pyinstaller==6.22.3", package_dependencies)

    def test_release_workflow_is_tag_driven_and_has_write_permission(self):
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")

        self.assertIn("tags:", workflow)
        self.assertIn("v*", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("gh release create", workflow)

    def test_installer_uses_user_scope_and_expected_asset_name(self):
        installer = (ROOT / "packaging/windows/installer.iss").read_text(
            encoding="utf-8"
        )

        self.assertIn("PrivilegesRequired=lowest", installer)
        self.assertIn("DefaultDirName={code:GetDefaultDirName}", installer)
        self.assertIn("GetEnv('LOCALAPPDATA')", installer)
        self.assertIn("JingweiZhizao-Setup-", installer)

    def test_release_notes_and_build_script_exist(self):
        notes = (ROOT / "docs/releases/v0.1.3.md").read_text(encoding="utf-8")
        script = (ROOT / "scripts/build_release.ps1").read_text(encoding="utf-8-sig")

        self.assertIn("v0.1.3", notes)
        self.assertIn("JingweiZhizao-Portable-", script)
        self.assertIn("Get-FileHash", script)

    def test_readme_links_to_latest_release(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("releases/latest", readme)


if __name__ == "__main__":
    unittest.main()