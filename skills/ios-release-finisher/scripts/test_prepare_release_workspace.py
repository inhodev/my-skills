#!/usr/bin/env python3

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("prepare_release_workspace.py")
SPEC = importlib.util.spec_from_file_location("prepare_release_workspace", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PrepareReleaseWorkspaceTests(unittest.TestCase):
    def make_flutter_project(self, root: Path) -> None:
        (root / "ios" / "Runner").mkdir(parents=True)
        (root / "ios" / "Runner.xcodeproj").mkdir(parents=True)
        (root / "pubspec.yaml").write_text(
            "name: sample_app\nversion: 1.2.3+17\n",
            encoding="utf-8",
        )
        (root / "ios" / "Runner.xcodeproj" / "project.pbxproj").write_text(
            "PRODUCT_BUNDLE_IDENTIFIER = com.example.sample;\n"
            "DEVELOPMENT_TEAM = ABCDE12345;\n",
            encoding="utf-8",
        )
        (root / "ios" / "Runner" / "Info.plist").write_text(
            "<plist><dict>"
            "<key>CFBundleDisplayName</key><string>Sample</string>"
            "<key>NSCameraUsageDescription</key><string>사진 촬영에 사용합니다.</string>"
            "</dict></plist>",
            encoding="utf-8",
        )
        (root / "ios" / "Runner" / "PrivacyInfo.xcprivacy").write_text(
            "<plist><dict><key>NSPrivacyTracking</key><false/></dict></plist>",
            encoding="utf-8",
        )

    def test_detects_identity_without_exposing_values_as_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_flutter_project(root)

            state = MODULE.inspect_project(root)

            self.assertEqual(state["project"]["stack"], "flutter")
            self.assertEqual(state["project"]["bundle_ids"], ["com.example.sample"])
            self.assertEqual(state["project"]["marketing_version"], "1.2.3")
            self.assertEqual(state["project"]["build_number"], "17")
            self.assertIn("NSCameraUsageDescription", state["evidence"]["usage_descriptions"])
            self.assertTrue(state["evidence"]["privacy_manifest_files"])

            deferred = {item["id"] for item in state["deferred_inputs"]}
            self.assertIn("privacy_contact", deferred)
            self.assertIn("pricing_and_territories", deferred)
            self.assertIn("age_rating_approval", deferred)
            self.assertEqual(state["release_blocks"], [])

    def test_generates_complete_packet_without_overwriting_existing_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_flutter_project(root)
            output = root / ".ios-release-finisher"

            created = MODULE.prepare_workspace(root, output)
            expected = {
                "RELEASE_READINESS_REPORT.md",
                "APP_STORE_METADATA_DRAFT.md",
                "PRIVACY_AND_LEGAL_AUDIT.md",
                "AGE_RATING_DRAFT.md",
                "SCREENSHOT_PLAN.md",
                "PORTAL_ACTIONS.md",
                "FINAL_INPUT_REQUEST.md",
                "RELEASE_STATE.json",
            }
            self.assertEqual({path.name for path in created}, expected)

            state = json.loads((output / "RELEASE_STATE.json").read_text(encoding="utf-8"))
            self.assertEqual(state["project"]["bundle_ids"], ["com.example.sample"])
            self.assertEqual(state["workflow_state"], "LOCAL_PREPARATION_IN_PROGRESS")

            metadata = output / "APP_STORE_METADATA_DRAFT.md"
            metadata.write_text("user-owned draft\n", encoding="utf-8")
            MODULE.prepare_workspace(root, output)
            self.assertEqual(metadata.read_text(encoding="utf-8"), "user-owned draft\n")

    def test_missing_ios_surface_is_a_release_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("not an app\n", encoding="utf-8")

            state = MODULE.inspect_project(root)

            self.assertEqual(state["project"]["stack"], "unknown")
            self.assertEqual(state["release_blocks"][0]["id"], "ios_project_not_found")

    def test_ignores_vendor_samples_archives_and_generated_packets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sample = root / "vendor" / "tool" / "Sample.xcodeproj"
            sample.mkdir(parents=True)
            (sample / "project.pbxproj").write_text(
                "PRODUCT_BUNDLE_IDENTIFIER = com.vendor.sample;\n",
                encoding="utf-8",
            )
            archive = root / ".launcher-build" / "Old.xcarchive" / "Products" / "Old.app"
            archive.mkdir(parents=True)
            (archive / "Info.plist").write_text(
                "<plist><dict><key>CFBundleDisplayName</key><string>Old</string></dict></plist>",
                encoding="utf-8",
            )
            generated = root / ".ios-release-finisher"
            generated.mkdir()
            (generated / "Evidence.plist").write_text(
                "<plist><dict><key>CFBundleName</key><string>Generated</string></dict></plist>",
                encoding="utf-8",
            )

            state = MODULE.inspect_project(root)

            self.assertEqual(state["project"]["stack"], "unknown")
            self.assertEqual(state["project"]["bundle_ids"], [])
            self.assertEqual(state["project"]["display_names"], [])


if __name__ == "__main__":
    unittest.main()
