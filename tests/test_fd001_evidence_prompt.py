from __future__ import annotations

import math
import re
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

from web.server import create_server


ROOT = Path(__file__).resolve().parents[1]
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


class FD001EvidencePromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not EDGE.is_file():
            raise RuntimeError("Microsoft Edge browser executable is unavailable.")
        cls.server = create_server(port=0, project_root=ROOT)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=str(EDGE), headless=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self) -> None:
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1000})
        self.context.grant_permissions(["clipboard-read", "clipboard-write"], origin=self.base)
        self.page = self.context.new_page()
        self.page.goto(self.base, wait_until="domcontentloaded")
        self.ready()

    def tearDown(self) -> None:
        self.context.close()

    def ready(self) -> None:
        self.page.locator("#ui-state", has_text="資料已就緒").wait_for()

    def select_range(self, split: str, unit: int, start: int, end: int, cycle: int, sensor: str) -> None:
        if self.page.locator("#split-select").input_value() != split:
            self.page.select_option("#split-select", split)
            self.ready()
        if self.page.locator("#unit-select").input_value() != str(unit):
            self.page.select_option("#unit-select", str(unit))
            self.ready()
        self.page.select_option("#start-cycle-select", str(start))
        self.ready()
        self.page.select_option("#end-cycle-select", str(end))
        self.ready()
        self.page.select_option("#cycle-select", str(cycle))
        self.ready()
        self.page.select_option("#sensor-select", sensor)
        self.ready()

    def prompt(self) -> str:
        self.page.click("#generate-prompt")
        self.page.locator("#prompt-preview[data-valid='true']").wait_for()
        return self.page.locator("#prompt-preview").input_value()

    def test_01_default_range_is_complete_actual_cycle_set(self) -> None:
        cycles = self.page.locator("#cycle-select option").all_text_contents()
        self.assertEqual(self.page.locator("#start-cycle-select").input_value(), cycles[0])
        self.assertEqual(self.page.locator("#end-cycle-select").input_value(), cycles[-1])
        self.assertEqual(self.page.locator("#range-badge").inner_text(), f"Cycle {cycles[0]}–{cycles[-1]} · {len(cycles)} samples")

    def test_02_range_boundaries_correct_selected_cycle(self) -> None:
        self.page.select_option("#end-cycle-select", "10")
        self.ready()
        self.page.select_option("#start-cycle-select", "20")
        self.ready()
        self.assertEqual(self.page.locator("#start-cycle-select").input_value(), "20")
        self.assertEqual(self.page.locator("#end-cycle-select").input_value(), "20")
        self.assertEqual(self.page.locator("#cycle-select option").all_text_contents(), ["20"])
        self.assertEqual(self.page.locator("#cycle-select").input_value(), "20")

    def test_03_nonconstant_range_statistics_and_order(self) -> None:
        self.select_range("train", 1, 90, 100, 96, "sensor_02")
        series = self.page.request.get(self.base + "/api/v1/sensor-series?split=train&unit_id=1&sensor_id=sensor_02").json()["data"]
        points = [point for point in series["points"] if 90 <= point["cycle"] <= 100]
        self.assertEqual([point["cycle"] for point in points], list(range(90, 101)))
        rendered = self.page.locator("#range-stats").inner_text()
        self.assertIn("Samples\n11", rendered)
        self.assertIn("Actual range\n90–100", rendered)
        self.assertIn(str(points[0]["value"]), rendered)
        self.assertIn(str(points[-1]["value"]), rendered)
        path = self.page.locator("#trend-chart .chart-line").get_attribute("d")
        self.assertEqual(len(re.findall(r"[ML]", path or "")), 11)

    def test_04_single_cycle_constant_svg_is_finite(self) -> None:
        self.select_range("train", 1, 96, 96, 96, "sensor_01")
        path = self.page.locator("#trend-chart .chart-line").get_attribute("d")
        self.assertRegex(path or "", r"^M-?\d+\.\d{2},-?\d+\.\d{2}$")
        self.assertNotRegex(path or "", r"NaN|Infinity")
        dot = self.page.locator("#trend-chart .chart-dot")
        self.assertEqual(dot.count(), 1)
        self.assertTrue(math.isfinite(float(dot.get_attribute("cx"))))
        self.assertTrue(math.isfinite(float(dot.get_attribute("cy"))))
        self.assertIn("Samples\n1", self.page.locator("#range-stats").inner_text())

    def test_05_prompt_schema_locator_and_statistic_scopes(self) -> None:
        self.select_range("train", 1, 90, 100, 96, "sensor_01")
        prompt = self.prompt()
        for required in (
            "OBSERVED_DATA", "DERIVED_STATISTICS", "ANALYSIS_QUESTIONS", "LIMITATIONS",
            "FULL_UNIT_STATISTICS", "SELECTED_RANGE_STATISTICS", "raw_source_locator:",
            "raw_line_number=", "parsed_row_index=", "raw_column_index=6",
            "raw_token=518.67", "parsed_value=518.67", "sample_count=11",
            "STUDENT_TRUSTED_LOCAL_FILES", "UNVERIFIED",
        ):
            self.assertIn(required, prompt)

    def test_06_train_and_test_rul_semantics(self) -> None:
        self.select_range("train", 1, 90, 100, 96, "sensor_01")
        self.assertIn("train_rul: NOT_APPLICABLE", self.prompt())
        self.select_range("test", 100, 90, 110, 100, "sensor_02")
        prompt = self.prompt()
        expected = self.page.request.get(self.base + "/api/v1/test-rul?split=test&unit_id=100").json()["data"]["rul_cycles"]
        self.assertIn(f"test_rul_cycles: {expected}", prompt)
        self.assertIn("final observed cycle", prompt)
        self.assertIn("not arbitrary Selected Cycle 100", prompt)

    def test_07_selection_change_invalidates_prompt_and_copy(self) -> None:
        original = self.prompt()
        self.assertTrue(original)
        self.assertFalse(self.page.locator("#copy-prompt").is_disabled())
        self.page.select_option("#sensor-select", "sensor_02")
        self.assertEqual(self.page.locator("#prompt-preview").input_value(), "")
        self.assertTrue(self.page.locator("#copy-prompt").is_disabled())
        self.ready()
        self.assertTrue(self.page.locator("#copy-prompt").is_disabled())
        self.assertFalse(self.page.locator("#generate-prompt").is_disabled())

    def test_08_actual_clipboard_content_and_bounded_prompt(self) -> None:
        self.select_range("test", 100, 90, 110, 100, "sensor_02")
        prompt = self.prompt()
        self.page.click("#copy-prompt")
        self.page.locator("#prompt-status", has_text="成功複製").wait_for()
        copied = self.page.evaluate("navigator.clipboard.readText()")
        self.assertEqual(copied.replace("\r\n", "\n"), prompt.replace("\r\n", "\n"))
        self.assertNotIn('"points"', prompt)
        self.assertNotIn("sensor_series", prompt.lower())
        self.assertLess(len(prompt.splitlines()), 45)


if __name__ == "__main__":
    unittest.main()
