from __future__ import annotations

import re
import tempfile
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

from web.server import create_server


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "FD001"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
SCREENSHOTS = Path(tempfile.gettempdir()) / "NTUST_FD001_M4_EVIDENCE"
SVG_WIDTH, SVG_HEIGHT = 900.0, 350.0
PAD = {"left": 68.0, "right": 28.0, "top": 24.0, "bottom": 48.0}


def raw_rows(split: str) -> list[dict[str, object]]:
    """Independent oracle built directly from the authorized TXT source."""
    rows: list[dict[str, object]] = []
    parsed_index = 0
    for line_number, line in enumerate((DATA / f"{split}_FD001.txt").read_text(encoding="ascii").splitlines(), start=1):
        tokens = line.split()
        if not tokens:
            continue
        values = [float(token) for token in tokens]
        rows.append({
            "tokens": tokens,
            "values": values,
            "line": line_number,
            "index": parsed_index,
            "unit": int(values[0]),
            "cycle": int(values[1]),
        })
        parsed_index += 1
    return rows


class FD001M4BrowserUAT(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not EDGE.is_file():
            raise RuntimeError("Microsoft Edge browser executable is unavailable.")
        SCREENSHOTS.mkdir(parents=True, exist_ok=True)
        cls.raw = {split: raw_rows(split) for split in ("train", "test")}
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
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1100})
        self.context.grant_permissions(["clipboard-read", "clipboard-write"], origin=self.base)
        self.page = self.context.new_page()
        self.console_errors: list[str] = []
        self.page.on("console", lambda message: self.console_errors.append(message.text) if message.type == "error" else None)
        self.page.goto(self.base, wait_until="domcontentloaded")
        self.ready()

    def tearDown(self) -> None:
        self.context.close()

    def ready(self) -> None:
        self.page.locator("#ui-state", has_text="資料已就緒").wait_for()

    def reload_with_script(self, script: str) -> None:
        self.context.add_init_script(script=script)
        self.page.reload(wait_until="domcontentloaded")
        self.ready()

    def unit_rows(self, split: str, unit: int) -> list[dict[str, object]]:
        return [row for row in self.raw[split] if row["unit"] == unit]

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

    @staticmethod
    def expected_coordinates(rows: list[dict[str, object]], column: int) -> list[tuple[float, float]]:
        xs = [row["cycle"] for row in rows]
        ys = [row["values"][column] for row in rows]
        min_x, max_x = xs[0], xs[-1]
        min_y, max_y = min(ys), max(ys)
        if min_y == max_y:
            margin = max(abs(min_y) * 0.01, 1.0)
            min_y -= margin
            max_y += margin
        plot_width = SVG_WIDTH - PAD["left"] - PAD["right"]
        plot_height = SVG_HEIGHT - PAD["top"] - PAD["bottom"]
        return [
            (
                PAD["left"] + (x - min_x) / max(1, max_x - min_x) * plot_width,
                PAD["top"] + (max_y - y) / (max_y - min_y) * plot_height,
            )
            for x, y in zip(xs, ys)
        ]

    def assert_case(self, split: str, unit: int, sensor: str, column: int, start: int, end: int, cycle: int, screenshot: str) -> None:
        self.select_range(split, unit, start, end, cycle, sensor)
        raw_range = [row for row in self.unit_rows(split, unit) if start <= row["cycle"] <= end]
        selected = next(row for row in raw_range if row["cycle"] == cycle)
        api_series = self.page.request.get(self.base + f"/api/v1/sensor-series?split={split}&unit_id={unit}&sensor_id={sensor}").json()["data"]
        api_points = [point for point in api_series["points"] if start <= point["cycle"] <= end]
        self.assertEqual(len(api_points), len(raw_range))
        for raw, point in zip(raw_range, api_points):
            self.assertEqual(point["cycle"], raw["cycle"])
            self.assertEqual(point["value"], raw["values"][column])
            self.assertEqual(point["raw_value"], raw["tokens"][column])
        self.assertEqual(float(self.page.locator("#selected-value").inner_text()), selected["values"][column])
        locator = self.page.locator("#locator-detail").inner_text()
        for expected in (str(selected["line"]), str(selected["index"]), str(column + 1), selected["tokens"][column]):
            self.assertIn(expected, locator)
        actual_path = [
            (float(x), float(y))
            for _, x, y in re.findall(r"([ML])(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)", self.page.locator("#trend-chart .chart-line").get_attribute("d") or "")
        ]
        expected_path = self.expected_coordinates(raw_range, column)
        self.assertEqual(len(actual_path), len(expected_path))
        for actual, expected in zip(actual_path, expected_path):
            self.assertAlmostEqual(actual[0], expected[0], delta=0.0051)
            self.assertAlmostEqual(actual[1], expected[1], delta=0.0051)
        selected_index = next(index for index, row in enumerate(raw_range) if row["cycle"] == cycle)
        dot = self.page.locator("#trend-chart .chart-dot")
        self.assertAlmostEqual(float(dot.get_attribute("cx")), expected_path[selected_index][0], delta=1e-9)
        self.assertAlmostEqual(float(dot.get_attribute("cy")), expected_path[selected_index][1], delta=1e-9)
        prompt = self.prompt()
        for expected in (
            f"split={split}", f"unit={unit}", f"start_cycle={start}", f"end_cycle={end}",
            f"selected_cycle={cycle}", f"sensor={sensor}", f"sample_count={len(raw_range)}",
            f"raw_line_number={selected['line']}", f"parsed_row_index={selected['index']}",
            f"raw_column_index={column + 1}", f"raw_token={selected['tokens'][column]}",
        ):
            self.assertIn(expected, prompt)
        self.page.screenshot(path=str(SCREENSHOTS / screenshot), full_page=True)

    def test_uat_m4_01_real_site_and_http_api_start(self) -> None:
        response = self.page.request.get(self.base + "/api/v1/status")
        self.assertEqual(response.status, 200)
        self.assertTrue(response.json()["data"]["data_available"])
        self.assertEqual(self.page.title(), "FD001 Health Analytics")
        self.page.screenshot(path=str(SCREENSHOTS / "m4_overview.png"), full_page=True)

    def test_uat_m4_02_train_test_namespace_separation(self) -> None:
        train = self.page.request.get(self.base + "/api/v1/raw-row?split=train&unit_id=1&cycle=1").json()["data"]
        self.page.select_option("#split-select", "test")
        self.ready()
        test = self.page.request.get(self.base + "/api/v1/raw-row?split=test&unit_id=1&cycle=1").json()["data"]
        self.assertNotEqual(train["source_locator"]["source_sha256"], test["source_locator"]["source_sha256"])
        self.assertIn("TEST", self.page.locator("#selection-summary").inner_text())

    def test_uat_m4_03_engine_unit_rebuilds_valid_cycles(self) -> None:
        self.page.select_option("#unit-select", "100")
        self.ready()
        expected = [str(row["cycle"]) for row in self.unit_rows("train", 100)]
        self.assertEqual(self.page.locator("#start-cycle-select option").all_text_contents(), expected)
        self.assertEqual(self.page.locator("#end-cycle-select option").all_text_contents(), expected)
        self.assertEqual(self.page.locator("#cycle-select option").all_text_contents(), expected)

    def test_uat_m4_04_range_sample_count_and_selected_boundary(self) -> None:
        self.select_range("train", 1, 90, 100, 96, "sensor_02")
        self.assertEqual(self.page.locator("#cycle-select option").all_text_contents(), [str(cycle) for cycle in range(90, 101)])
        self.assertIn("11 samples", self.page.locator("#range-badge").inner_text())
        self.page.select_option("#end-cycle-select", "95")
        self.ready()
        self.assertEqual(self.page.locator("#cycle-select").input_value(), "95")

    def test_uat_m4_05_sensor_switch_updates_range_trend(self) -> None:
        self.select_range("train", 1, 90, 100, 96, "sensor_01")
        before = self.page.locator("#trend-chart .chart-line").get_attribute("d")
        self.page.select_option("#sensor-select", "sensor_02")
        self.ready()
        after = self.page.locator("#trend-chart .chart-line").get_attribute("d")
        self.assertNotEqual(before, after)
        self.assertIn("sensor_02", self.page.locator("#chart-title").inner_text())

    def test_uat_m4_06_case_a_api_raw_dom_svg_prompt(self) -> None:
        self.assert_case("test", 100, "sensor_02", 6, 90, 110, 100, "case_a.png")

    def test_uat_m4_07_case_b_constant_and_single_point_svg(self) -> None:
        self.assert_case("train", 1, "sensor_01", 5, 90, 100, 96, "case_b.png")
        self.select_range("train", 1, 96, 96, 96, "sensor_01")
        path = self.page.locator("#trend-chart .chart-line").get_attribute("d") or ""
        self.assertNotRegex(path, r"NaN|Infinity")
        self.assertEqual(len(re.findall(r"[ML]", path)), 1)

    def test_uat_m4_08_prompt_preview_and_actual_copy(self) -> None:
        self.select_range("test", 100, 90, 110, 100, "sensor_02")
        prompt = self.prompt()
        self.page.click("#copy-prompt")
        self.page.locator("#prompt-status", has_text="成功複製").wait_for()
        copied = self.page.evaluate("navigator.clipboard.readText()")
        self.assertEqual(copied.replace("\r\n", "\n"), prompt.replace("\r\n", "\n"))

    def test_uat_m4_09_prompt_invalidates_on_selection_change(self) -> None:
        self.assertTrue(self.prompt())
        self.page.select_option("#sensor-select", "sensor_02")
        self.assertEqual(self.page.locator("#prompt-preview").input_value(), "")
        self.assertTrue(self.page.locator("#copy-prompt").is_disabled())
        self.ready()
        current = self.prompt()
        self.assertIn("sensor=sensor_02", current)

    def test_uat_m4_10_invalid_empty_unavailable_and_integrity_errors(self) -> None:
        self.page.select_option("#end-cycle-select", "10")
        self.ready()
        self.page.select_option("#start-cycle-select", "20")
        self.ready()
        self.assertEqual(self.page.locator("#end-cycle-select").input_value(), "20")

        def empty(route):
            route.fulfill(status=200, content_type="application/json", body='{"ok":true,"data":{"points":[],"cycle_start":null,"cycle_end":null,"sample_count":0},"error":null}')
        self.page.route("**/api/v1/sensor-series?*", empty)
        self.page.select_option("#sensor-select", "sensor_02")
        self.page.locator("#error-panel[data-error-kind='empty-result']").wait_for()
        self.page.unroute("**/api/v1/sensor-series?*", empty)

        self.page.reload(wait_until="domcontentloaded")
        self.ready()
        self.page.route("**/api/v1/raw-row?*", lambda route: route.abort())
        self.page.select_option("#cycle-select", "2")
        self.page.locator("#error-panel[data-error-kind='api-unavailable']").wait_for()
        self.page.unroute("**/api/v1/raw-row?*")

        self.page.reload(wait_until="domcontentloaded")
        self.ready()
        self.page.route("**/api/v1/raw-row?*", lambda route: route.fulfill(status=503, content_type="application/json", body='{"ok":false,"data":null,"error":{"code":"SOURCE_INTEGRITY_FAILURE","message":"isolated integrity failure"}}'))
        self.page.select_option("#cycle-select", "2")
        self.page.locator("#error-panel[data-error-kind='source-integrity']").wait_for()
        self.assertTrue(self.page.locator("#generate-prompt").is_disabled())

    def test_uat_m4_11_test_rul_basis_and_train_absence(self) -> None:
        self.select_range("test", 100, 90, 110, 100, "sensor_02")
        self.assertTrue(self.page.locator("#rul-panel").is_visible())
        self.assertIn("final observed cycle", self.prompt())
        self.page.select_option("#split-select", "train")
        self.ready()
        self.assertFalse(self.page.locator("#rul-panel").is_visible())
        self.assertIn("train_rul: NOT_APPLICABLE", self.prompt())

    def test_uat_m4_12_controlled_stale_success_and_error_isolation(self) -> None:
        self.reload_with_script("""
            (() => {
              const nativeFetch = window.fetch.bind(window);
              window.fetch = async (input, init = {}) => {
                const url = typeof input === 'string' ? input : input.url;
                if (url.includes('/raw-row?') && url.includes('cycle=2')) {
                  await new Promise(resolve => setTimeout(resolve, 650));
                  document.documentElement.dataset.m4StaleErrorReleased = 'true';
                  return new Response(JSON.stringify({ok:false,data:null,error:{code:'INVALID_CYCLE',message:'stale M4 error'}}), {status:400,headers:{'Content-Type':'application/json'}});
                }
                const detached = {...init}; delete detached.signal;
                const response = await nativeFetch(input, detached);
                if (url.includes('sensor_02') || url.includes('cycle=2')) await new Promise(resolve => setTimeout(resolve, 550));
                if (url.includes('sensor_03') || url.includes('cycle=3')) await new Promise(resolve => setTimeout(resolve, 20));
                return response;
              };
            })();
        """)
        self.page.select_option("#sensor-select", "sensor_02")
        self.page.select_option("#cycle-select", "2")
        self.page.select_option("#sensor-select", "sensor_03")
        self.page.select_option("#cycle-select", "3")
        self.ready()
        self.page.locator("html[data-m4-stale-error-released='true']").wait_for()
        self.assertTrue(self.page.locator("#error-panel").is_hidden())
        self.assertEqual(self.page.locator("#cycle-select").input_value(), "3")
        self.assertIn("sensor_03", self.page.locator("#chart-title").inner_text())
        self.assertIn("selected_cycle=3", self.prompt())

    def test_uat_m4_13_console_clean_and_existing_evidence_visible(self) -> None:
        self.select_range("train", 50, 90, 100, 100, "sensor_21")
        self.assertEqual(self.console_errors, [])
        self.assertEqual(self.page.locator("#field-table tr").count(), 26)
        self.assertIn("data/FD001/train_FD001.txt", self.page.locator("#locator-detail").inner_text())
        self.assertIn("FULL_UNIT_STATISTICS", self.page.locator(".chart-panel").inner_text())


if __name__ == "__main__":
    unittest.main()
