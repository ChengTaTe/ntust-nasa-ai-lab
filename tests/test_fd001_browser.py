from __future__ import annotations

import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

from web.server import create_server


ROOT = Path(__file__).resolve().parents[1]
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


class FD001BrowserUAT(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server(port=0, project_root=ROOT)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.playwright = sync_playwright().start()
        if not EDGE.is_file():
            raise RuntimeError("Microsoft Edge browser executable is unavailable.")
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
        self.console_errors: list[str] = []
        self.page.on("console", lambda message: self.console_errors.append(message.text) if message.type == "error" else None)
        self.page.goto(self.base, wait_until="domcontentloaded")
        self.page.locator("#ui-state").wait_for(state="visible")
        self.page.locator("#ui-state", has_text="資料已就緒").wait_for()

    def tearDown(self) -> None:
        self.context.close()

    def ready(self) -> None:
        self.page.locator("#ui-state", has_text="資料已就緒").wait_for()

    def test_uat_01_site_loads(self) -> None:
        self.assertEqual(self.page.title(), "FD001 Health Analytics")
        self.assertEqual(self.page.locator("#validation-status").inner_text(), "LOCAL_DATA_VERIFIED")

    def test_uat_02_train_test_switch(self) -> None:
        self.page.select_option("#split-select", "test")
        self.ready()
        self.assertEqual(self.page.locator("#split-select").input_value(), "test")
        self.assertTrue(self.page.locator("#rul-panel").is_visible())

    def test_uat_03_engine_unit_selection(self) -> None:
        self.page.select_option("#unit-select", "50")
        self.ready()
        self.assertIn("50", self.page.locator("#selection-summary").inner_text())

    def test_uat_04_cycle_selection_and_range(self) -> None:
        cycles = self.page.locator("#cycle-select option").all_text_contents()
        self.page.select_option("#cycle-select", cycles[-1])
        self.ready()
        self.assertEqual(self.page.locator("#cycle-select").input_value(), cycles[-1])
        self.assertIn(cycles[-1], self.page.locator("#selection-summary").inner_text())

    def test_uat_05_all_21_sensors_selectable(self) -> None:
        sensors = self.page.locator("#sensor-select option").all_text_contents()
        self.assertEqual(sensors, [f"sensor_{index:02d}" for index in range(1, 22)])
        self.page.select_option("#sensor-select", "sensor_21")
        self.ready()
        self.assertEqual(self.page.locator("#selected-sensor").inner_text(), "sensor_21")

    def test_uat_06_sensor_value_matches_api(self) -> None:
        response = self.page.request.get(self.base + "/api/v1/raw-row?split=train&unit_id=1&cycle=1")
        expected = response.json()["data"]["fields"]["sensor_01"]["parsed_value"]
        self.assertEqual(float(self.page.locator("#selected-value").inner_text()), expected)

    def test_uat_07_sensor_trend_updates(self) -> None:
        before = self.page.locator("#trend-chart .chart-line").get_attribute("d")
        self.page.select_option("#sensor-select", "sensor_02")
        self.ready()
        after = self.page.locator("#trend-chart .chart-line").get_attribute("d")
        self.assertNotEqual(before, after)
        self.assertIn("sensor_02", self.page.locator("#chart-title").inner_text())

    def test_uat_08_raw_locator(self) -> None:
        text = self.page.locator("#locator-detail").inner_text()
        for expected in ("data/FD001/train_FD001.txt", "raw_line_number", "raw_column_index", "518.67"):
            self.assertIn(expected, text)

    def test_uat_09_operational_settings(self) -> None:
        response = self.page.request.get(self.base + "/api/v1/operational-settings?split=train&unit_id=1&cycle=1").json()["data"]
        rendered = self.page.locator("#op-settings strong").all_text_contents()
        self.assertEqual([float(value) for value in rendered], [response[f"op_setting_{index}"] for index in range(1, 4)])

    def test_uat_10_test_rul(self) -> None:
        self.page.select_option("#split-select", "test")
        self.ready()
        expected = self.page.request.get(self.base + "/api/v1/test-rul?split=test&unit_id=1").json()["data"]["rul_cycles"]
        self.assertEqual(self.page.locator("#rul-value").inner_text(), f"{expected} cycles")

    def test_uat_11_train_has_no_rul(self) -> None:
        self.assertFalse(self.page.locator("#rul-panel").is_visible())

    def test_uat_12_api_failure_is_visible(self) -> None:
        def fail_raw(route):
            route.fulfill(status=503, content_type="application/json", body='{"ok":false,"data":null,"error":{"code":"SOURCE_INTEGRITY_FAILURE","message":"Test integrity failure"}}')
        self.page.route("**/api/v1/raw-row?*", fail_raw)
        self.page.select_option("#cycle-select", "2")
        self.page.locator("#error-panel").wait_for(state="visible")
        self.assertIn("SOURCE_INTEGRITY_FAILURE", self.page.locator("#error-panel").inner_text())

    def test_uat_13_rapid_switch_has_no_stale_data(self) -> None:
        self.page.select_option("#unit-select", "2")
        self.page.select_option("#unit-select", "3")
        self.ready()
        self.assertEqual(self.page.locator("#unit-select").input_value(), "3")
        summary = self.page.locator("#selection-summary").inner_text()
        self.assertRegex(summary, r"Engine Unit\s+3")

    def test_uat_14_constant_sensor_and_undefined_stat(self) -> None:
        self.assertEqual(self.page.locator("#selected-sensor").inner_text(), "sensor_01")
        stats = self.page.locator("#trend-stats").inner_text()
        self.assertIn("Direction\nflat", stats)
        self.assertIn("Pearson r\nUNDEFINED", stats)
        self.assertIsNotNone(self.page.locator("#trend-chart .chart-line").get_attribute("d"))

    def test_uat_15_no_unhandled_console_error(self) -> None:
        self.page.select_option("#sensor-select", "sensor_02")
        self.ready()
        self.assertEqual(self.console_errors, [])


if __name__ == "__main__":
    unittest.main()
