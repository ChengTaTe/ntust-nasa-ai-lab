from __future__ import annotations

import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

from web.server import create_server


ROOT = Path(__file__).resolve().parents[1]
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


class FD001BrowserIntegrationTests(unittest.TestCase):
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
        self.page = self.context.new_page()
        self.page.goto(self.base, wait_until="domcontentloaded")
        self.ready()

    def tearDown(self) -> None:
        self.context.close()

    def ready(self) -> None:
        self.page.locator("#ui-state", has_text="資料已就緒").wait_for()

    def select(self, split: str, unit: int, cycle: int, sensor: str) -> None:
        self.page.select_option("#split-select", split)
        self.ready()
        self.page.select_option("#unit-select", str(unit))
        self.ready()
        self.page.select_option("#cycle-select", str(cycle))
        self.ready()
        self.page.select_option("#sensor-select", sensor)
        self.ready()

    def test_01_api_dom_locator_and_operational_settings(self) -> None:
        self.select("train", 50, 100, "sensor_21")
        row = self.page.request.get(self.base + "/api/v1/raw-row?split=train&unit_id=50&cycle=100").json()["data"]
        ops = self.page.request.get(self.base + "/api/v1/operational-settings?split=train&unit_id=50&cycle=100").json()["data"]
        locator = self.page.request.get(self.base + "/api/v1/raw-source-locator?split=train&unit_id=50&cycle=100&field_name=sensor_21").json()["data"]
        self.assertEqual(float(self.page.locator("#selected-value").inner_text()), row["fields"]["sensor_21"]["parsed_value"])
        self.assertEqual([float(value) for value in self.page.locator("#op-settings strong").all_text_contents()], [ops[f"op_setting_{i}"] for i in range(1, 4)])
        rendered_locator = self.page.locator("#locator-detail").inner_text()
        for value in (locator["source_file"], str(locator["raw_line_number"]), str(locator["raw_column_index"]), locator["raw_value"]):
            self.assertIn(value, rendered_locator)

    def test_02_svg_series_and_statistical_mapping(self) -> None:
        self.select("test", 100, 100, "sensor_02")
        series = self.page.request.get(self.base + "/api/v1/sensor-series?split=test&unit_id=100&sensor_id=sensor_02").json()["data"]
        trend = self.page.request.get(self.base + "/api/v1/sensor-trend?split=test&unit_id=100&sensor_id=sensor_02").json()["data"]
        path = self.page.locator("#trend-chart .chart-line").get_attribute("d")
        self.assertIsNotNone(path)
        self.assertEqual(path.count("L") + 1, series["sample_count"])
        self.assertEqual(self.page.locator("#trend-chart .chart-dot").count(), 1)
        rendered = self.page.locator("#trend-stats").inner_text()
        for expected in (str(trend["sample_count"]), f"{trend['cycle_start']}–{trend['cycle_end']}", trend["direction"]):
            self.assertIn(expected, rendered)

    def test_03_test_rul_and_train_absence(self) -> None:
        self.select("test", 100, 100, "sensor_01")
        rul = self.page.request.get(self.base + "/api/v1/test-rul?split=test&unit_id=100").json()["data"]["rul_cycles"]
        self.assertTrue(self.page.locator("#rul-panel").is_visible())
        self.assertEqual(self.page.locator("#rul-value").inner_text(), f"{rul} cycles")
        self.page.select_option("#split-select", "train")
        self.ready()
        self.assertFalse(self.page.locator("#rul-panel").is_visible())

    def test_04_error_is_not_rendered_as_normal_data(self) -> None:
        def fail(route):
            route.fulfill(status=503, content_type="application/json", body='{"ok":false,"data":null,"error":{"code":"SOURCE_INTEGRITY_FAILURE","message":"isolated integration fault"}}')
        self.page.route("**/api/v1/raw-row?*", fail)
        self.page.select_option("#cycle-select", "2")
        panel = self.page.locator("#error-panel[data-error-kind='source-integrity']")
        panel.wait_for(state="visible")
        self.assertIn("SOURCE_INTEGRITY_FAILURE", panel.inner_text())
        self.assertEqual(self.page.locator("#ui-state").get_attribute("data-state"), "error")
        self.assertEqual(self.page.locator("#selected-value").inner_text(), "—")


if __name__ == "__main__":
    unittest.main()
