from __future__ import annotations

import hashlib
import json
import math
import re
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

from web.server import create_server


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "FD001"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
EVIDENCE = Path(tempfile.gettempdir()) / "NTUST_FD001_M5_EVIDENCE"
CONTRACT = json.loads((ROOT / "contracts" / "FD001_DATA_CONTRACT.json").read_text(encoding="utf-8"))
IDENTITY = {item["dataset_split"]: item for item in CONTRACT["dataset_identity"]}
NAMES = ["unit_id", "cycle", "op_setting_1", "op_setting_2", "op_setting_3"] + [f"sensor_{index:02d}" for index in range(1, 22)]
SECTIONS = {"OBSERVED_DATA", "DERIVED_STATISTICS", "ANALYSIS_QUESTIONS", "LIMITATIONS"}


def raw_rows(split: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    parsed = 0
    for line_number, line in enumerate((DATA / f"{split}_FD001.txt").read_text(encoding="ascii").splitlines(), 1):
        tokens = line.split()
        if not tokens:
            continue
        values = [float(token) for token in tokens]
        rows.append({"tokens": tokens, "values": values, "line": line_number, "index": parsed, "unit": int(values[0]), "cycle": int(values[1])})
        parsed += 1
    return rows


def raw_rul() -> list[dict[str, object]]:
    rows = []
    for effective, (line_number, line) in enumerate((item for item in enumerate((DATA / "RUL_FD001.txt").read_text(encoding="ascii").splitlines(), 1) if item[1].split())):
        token = line.split()[0]
        rows.append({"line": line_number, "index": effective, "token": token, "value": int(float(token))})
    return rows


class FD001M5BrowserUAT(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not EDGE.is_file():
            raise RuntimeError("Microsoft Edge browser executable is unavailable.")
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        cls.raw = {split: raw_rows(split) for split in ("train", "test")}
        cls.rul = raw_rul()
        cls.raw_hash_before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in DATA.glob("*.txt")}
        cls.screenshots: dict[str, dict[str, str]] = {}
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
        after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in DATA.glob("*.txt")}
        if after != cls.raw_hash_before:
            raise AssertionError("Raw FD001 source hashes changed during M5 UAT.")
        (EVIDENCE / "manifest.json").write_text(json.dumps(cls.screenshots, indent=2, ensure_ascii=False), encoding="utf-8")

    def setUp(self) -> None:
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1100})
        self.context.grant_permissions(["clipboard-read", "clipboard-write"], origin=self.base)
        self.page = self.context.new_page()
        self.page_errors: list[str] = []
        self.console_errors: list[str] = []
        self.page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        self.page.on("console", lambda message: self.console_errors.append(message.text) if message.type == "error" else None)
        self.page.goto(self.base, wait_until="domcontentloaded")
        self.ready()

    def tearDown(self) -> None:
        self.context.close()

    def ready(self) -> None:
        self.page.locator("#ui-state", has_text="資料已就緒").wait_for()

    def capture(self, screenshot_id: str, state: str) -> None:
        path = EVIDENCE / f"{screenshot_id}.png"
        self.page.screenshot(path=str(path), full_page=True)
        self.screenshots[screenshot_id] = {
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "state": state,
            "file": path.name,
        }

    def unit_rows(self, split: str, unit: int) -> list[dict[str, object]]:
        return [row for row in self.raw[split] if row["unit"] == unit]

    def select(self, split: str, unit: int, start: int, end: int, cycle: int, sensor: str) -> None:
        if self.page.locator("#split-select").input_value() != split:
            self.page.select_option("#split-select", split)
            self.ready()
        if self.page.locator("#unit-select").input_value() != str(unit):
            self.page.select_option("#unit-select", str(unit))
            self.ready()
        for selector, value in (("#start-cycle-select", start), ("#end-cycle-select", end), ("#cycle-select", cycle), ("#sensor-select", sensor)):
            self.page.select_option(selector, str(value))
            self.ready()

    def definition_list(self, selector: str) -> dict[str, str]:
        keys = self.page.locator(f"{selector} dt").all_text_contents()
        values = self.page.locator(f"{selector} dd").all_text_contents()
        self.assertEqual(len(keys), len(values))
        self.assertEqual(len(keys), len(set(keys)))
        return dict(zip(keys, values))

    def statistics(self, selector: str) -> dict[str, str]:
        result = {}
        for item in self.page.locator(f"{selector} .stat").all():
            result[item.locator("span").inner_text()] = item.locator("strong").inner_text()
        return result

    def prompt(self) -> str:
        self.page.click("#generate-prompt")
        self.page.locator("#prompt-preview[data-valid='true']").wait_for()
        return self.page.locator("#prompt-preview").input_value()

    @staticmethod
    def prompt_sections(prompt: str) -> dict[str, list[str]]:
        result = {name: [] for name in SECTIONS}
        active = None
        for line in prompt.replace("\r\n", "\n").splitlines():
            if line in SECTIONS:
                active = line
            elif active and line:
                result[active].append(line)
        return result

    def prompt_line(self, sections: dict[str, list[str]], section: str, prefix: str) -> str:
        matches = [line[len(prefix):] for line in sections[section] if line.startswith(prefix)]
        self.assertEqual(len(matches), 1)
        return matches[0]

    @staticmethod
    def key_values(text: str, separator: str = "; ") -> dict[str, str]:
        return dict(item.split("=", 1) for item in text.split(separator))

    def display_float(self, actual: str, expected: float) -> None:
        tolerance = 5.1e-9 if expected == 0 else 0.51 * 10 ** (math.floor(math.log10(abs(expected))) - 7)
        self.assertAlmostEqual(float(actual), expected, delta=tolerance)

    @staticmethod
    def expected_coordinates(rows: list[dict[str, object]], column: int) -> list[tuple[float, float]]:
        xs = [row["cycle"] for row in rows]
        ys = [row["values"][column] for row in rows]
        minimum, maximum = min(ys), max(ys)
        if minimum == maximum:
            margin = max(abs(minimum) * 0.01, 1)
            minimum -= margin
            maximum += margin
        return [(68 + (x - xs[0]) / max(1, xs[-1] - xs[0]) * 804, 24 + (maximum - y) / (maximum - minimum) * 278) for x, y in zip(xs, ys)]

    def assert_raw_case(self, split: str, unit: int, sensor: str, start: int, end: int, cycle: int, screenshot: str | None = None) -> None:
        column = int(sensor[-2:]) + 4
        self.select(split, unit, start, end, cycle, sensor)
        selected = next(row for row in self.raw[split] if row["unit"] == unit and row["cycle"] == cycle)
        api = self.page.request.get(self.base + f"/api/v1/raw-row?split={split}&unit_id={unit}&cycle={cycle}").json()["data"]
        self.assertEqual((api["unit_id"], api["cycle"]), (unit, cycle))
        self.assertEqual(list(api["fields"]), NAMES)
        for index, name in enumerate(NAMES):
            field = api["fields"][name]
            self.assertEqual(field["raw_column_index"], index + 1)
            self.assertEqual(field["canonical_field_name"], name)
            self.assertEqual(field["raw_value"], selected["tokens"][index])
            self.assertEqual(field["parsed_value"], selected["values"][index])
            self.assertEqual((field["raw_line_number"], field["parsed_row_index"]), (selected["line"], selected["index"]))
        self.assertEqual(float(self.page.locator("#selected-value").inner_text()), selected["values"][column])
        rendered_ops = dict(zip(self.page.locator("#op-settings small").all_text_contents(), self.page.locator("#op-settings strong").all_text_contents()))
        self.assertEqual(set(rendered_ops), {"Setting 1", "Setting 2", "Setting 3"})
        for index in range(1, 4):
            self.assertEqual(float(rendered_ops[f"Setting {index}"]), selected["values"][index + 1])
        identity = IDENTITY[split]
        self.assertEqual(self.definition_list("#locator-detail"), {
            "dataset_id": identity["dataset_id"], "dataset_split": split, "source_file": identity["source_file"],
            "source_sha256": identity["source_sha256"], "raw_line_number": str(selected["line"]),
            "parsed_row_index": str(selected["index"]), "unit_id": str(unit), "cycle": str(cycle),
            "raw_column_index": str(column + 1), "canonical_field_name": sensor,
            "raw_value": selected["tokens"][column], "parsed_value": str(selected["values"][column]),
        })
        if screenshot:
            self.capture(screenshot, f"{split} Unit {unit} Cycle {cycle} {sensor}")

    def assert_trend_prompt(self, split: str, unit: int, sensor: str, start: int, end: int, cycle: int) -> None:
        column = int(sensor[-2:]) + 4
        self.select(split, unit, start, end, cycle, sensor)
        full = self.unit_rows(split, unit)
        rows = [row for row in full if start <= row["cycle"] <= end]
        values = [row["values"][column] for row in rows]
        expected = {"Start": values[0], "End": values[-1], "Change": values[-1] - values[0], "Minimum": min(values), "Maximum": max(values), "Mean": sum(values) / len(values)}
        dom = self.statistics("#range-stats")
        self.assertEqual((int(dom["Samples"]), dom["Actual range"]), (len(rows), f"{start}–{end}"))
        for key, value in expected.items():
            self.display_float(dom[key], value)
        full_dom = self.statistics("#trend-stats")
        self.assertEqual((int(full_dom["Samples"]), full_dom["Cycle range"]), (len(full), f"{full[0]['cycle']}–{full[-1]['cycle']}"))
        path = [(float(x), float(y)) for _, x, y in re.findall(r"([ML])(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)", self.page.locator("#trend-chart .chart-line").get_attribute("d") or "")]
        coordinates = self.expected_coordinates(rows, column)
        self.assertEqual(len(path), len(coordinates))
        for actual, wanted in zip(path, coordinates):
            self.assertAlmostEqual(actual[0], wanted[0], delta=0.0051)
            self.assertAlmostEqual(actual[1], wanted[1], delta=0.0051)
        selected_index = next(index for index, row in enumerate(rows) if row["cycle"] == cycle)
        dot = self.page.locator("#trend-chart .chart-dot")
        self.assertAlmostEqual(float(dot.get_attribute("cx")), coordinates[selected_index][0], delta=1e-9)
        self.assertAlmostEqual(float(dot.get_attribute("cy")), coordinates[selected_index][1], delta=1e-9)
        sections = self.prompt_sections(self.prompt())
        self.assertEqual(set(sections), SECTIONS)
        selection = self.key_values(self.prompt_line(sections, "OBSERVED_DATA", "selection: "), ", ")
        self.assertEqual(selection, {"split": split, "unit": str(unit), "start_cycle": str(start), "end_cycle": str(end), "selected_cycle": str(cycle), "sensor": sensor})
        locator = self.key_values(self.prompt_line(sections, "OBSERVED_DATA", "raw_source_locator: "))
        self.assertEqual(locator["source_sha256"], IDENTITY[split]["source_sha256"])
        prompt_range = self.key_values(self.prompt_line(sections, "DERIVED_STATISTICS", "SELECTED_RANGE_STATISTICS: "))
        self.assertEqual((prompt_range["cycle_range"], int(prompt_range["sample_count"])), (f"{start}-{end}", len(rows)))
        for key, expected_key in (("start_value", "Start"), ("end_value", "End"), ("change", "Change"), ("minimum", "Minimum"), ("maximum", "Maximum"), ("arithmetic_mean", "Mean")):
            self.display_float(prompt_range[key], expected[expected_key])

    def new_fault_page(self, pattern: str, mutate, *, body_transform=None):
        context = self.browser.new_context(viewport={"width": 1440, "height": 1100})
        page = context.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))

        def handler(route):
            response = route.fetch()
            if body_transform:
                route.fulfill(response=response, body=body_transform(response.text()))
            else:
                payload = response.json()
                mutate(payload["data"])
                route.fulfill(response=response, json=payload)

        page.route(pattern, handler)
        page.goto(self.base, wait_until="domcontentloaded")
        page.locator("#error-panel[data-error-kind='malformed-response']").wait_for()
        return context, page, errors

    def assert_failed_closed(self, page, errors: list[str]) -> None:
        self.assertNotEqual(page.locator("#ui-state").inner_text(), "資料已就緒")
        self.assertEqual(page.locator("#prompt-preview").get_attribute("data-valid"), "false")
        self.assertEqual(page.locator("#prompt-preview").input_value(), "")
        self.assertTrue(page.locator("#generate-prompt").is_disabled())
        self.assertTrue(page.locator("#copy-prompt").is_disabled())
        self.assertEqual(page.locator("#selected-value").inner_text(), "—")
        self.assertEqual(page.locator("#trend-chart .chart-line").count(), 0)
        self.assertEqual(errors, [])

    def test_m5_01_startup_data_protection_and_controls(self) -> None:
        status = self.page.request.get(self.base + "/api/v1/status")
        self.assertEqual(status.status, 200)
        self.assertEqual(status.json()["data"]["validation_status"], "LOCAL_DATA_VERIFIED")
        self.assertEqual(self.page.title(), "FD001 Health Analytics")
        for selector in ("#split-select", "#unit-select", "#start-cycle-select", "#end-cycle-select", "#cycle-select", "#sensor-select"):
            self.assertTrue(self.page.locator(selector).is_enabled())
        self.assertEqual(self.page.request.get(self.base + "/../AGENTS.md").status, 404)
        self.assertEqual(self.raw_hash_before, {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in DATA.glob("*.txt")})
        self.capture("S01", "Successful website startup and LOCAL_DATA_VERIFIED")

    def test_m5_02_dataset_unit_cycle_and_sensor_workflow(self) -> None:
        for split in ("train", "test", "train"):
            self.page.select_option("#split-select", split)
            self.ready()
            units = self.page.request.get(self.base + f"/api/v1/units?split={split}").json()["data"]["units"]
            self.assertEqual([int(value) for value in self.page.locator("#unit-select option").all_text_contents()], units)
        self.page.select_option("#unit-select", "50")
        self.ready()
        cycles = [row["cycle"] for row in self.unit_rows("train", 50)]
        self.assertEqual([int(value) for value in self.page.locator("#cycle-select option").all_text_contents()], cycles)
        for cycle in (cycles[0], cycles[len(cycles) // 2], cycles[-1]):
            self.page.select_option("#cycle-select", str(cycle))
            self.ready()
            self.assertEqual(int(self.definition_list("#selection-summary")["Cycle"]), cycle)
        self.assertEqual(self.page.locator("#sensor-select option").all_text_contents(), [f"sensor_{index:02d}" for index in range(1, 22)])
        for sensor in ("sensor_01", "sensor_02", "sensor_21"):
            self.page.select_option("#sensor-select", sensor)
            self.ready()
            self.assertEqual(self.definition_list("#locator-detail")["canonical_field_name"], sensor)

    def test_m5_03_cases_a_b_c_d_exact_raw_rows(self) -> None:
        self.assert_raw_case("test", 100, "sensor_02", 90, 110, 100, "S02")
        self.assert_raw_case("train", 1, "sensor_01", 90, 100, 96, "S03")
        self.assert_raw_case("train", 1, "sensor_01", 96, 96, 96, "S04")
        self.assert_raw_case("test", 50, "sensor_21", 74, 74, 74)

    def test_m5_04_cases_a_b_c_d_trend_svg_and_prompt(self) -> None:
        for case in (("test", 100, "sensor_02", 90, 110, 100), ("train", 1, "sensor_01", 90, 100, 96), ("train", 1, "sensor_01", 96, 96, 96), ("test", 50, "sensor_21", 74, 74, 74)):
            with self.subTest(case=case):
                self.assert_trend_prompt(*case)
        self.capture("S09", "CASE D valid four-section Evidence Prompt preview")

    def test_m5_05_direct_http_invalid_queries_and_browser_error(self) -> None:
        cases = (
            ("/api/v1/units?split=bad", 400, "INVALID_SPLIT", "Unsupported split: bad"),
            ("/api/v1/cycles?split=train&unit_id=999", 404, "UNKNOWN_UNIT", "Unknown unit 999 in train."),
            ("/api/v1/raw-row?split=train&unit_id=1&cycle=9999", 400, "INVALID_CYCLE", "Cycle 9999 does not exist for unit 1."),
            ("/api/v1/sensor-trend?split=train&unit_id=1&sensor_id=sensor_99", 400, "UNKNOWN_SENSOR", "Unknown sensor: sensor_99"),
            ("/api/v1/units", 400, "INVALID_REQUEST", "A required query parameter is missing."),
            ("/api/v1/units?split=train&split=test", 400, "INVALID_REQUEST", "Query parameters must be present exactly once."),
            ("/api/v1/cycles?split=train&unit_id=abc", 400, "INVALID_REQUEST", "unit_id must be a positive integer."),
            ("/api/v1/test-rul?split=train&unit_id=1", 400, "UNSUPPORTED_RUL_QUERY", "Train RUL is not supplied by RUL_FD001.txt."),
        )
        for path, status, code, message in cases:
            with self.subTest(path=path):
                response = self.page.request.get(self.base + path)
                payload = response.json()
                self.assertEqual((response.status, payload["ok"], payload["data"], payload["error"]), (status, False, None, {"code": code, "message": message}))

        def controlled_error(route):
            route.fulfill(status=404, content_type="application/json", body='{"ok":false,"data":null,"error":{"code":"EMPTY_QUERY_RESULT","message":"controlled empty result"}}')

        self.page.route("**/api/v1/raw-row?*", controlled_error)
        self.page.select_option("#cycle-select", "2")
        self.page.locator("#error-panel[data-error-kind='empty-result']").wait_for()
        self.assertTrue(self.page.locator("#generate-prompt").is_disabled())
        self.assertTrue(self.page.locator("#copy-prompt").is_disabled())
        self.capture("S06", "Controlled browser empty-result error state")

    def test_m5_06_fault_matrix_f001_t01_to_t09_t19_t20(self) -> None:
        scenarios = [
            ("F001-T01", "**/api/v1/raw-row?*", lambda data: data["fields"]["sensor_01"].__setitem__("parsed_value", None), None),
            ("F001-T02", "**/api/v1/operational-settings?*", lambda data: data.__setitem__("op_setting_1", None), None),
            ("F001-T03", "**/api/v1/sensor-series?*", lambda data: data["points"][0].__setitem__("value", None), None),
            ("F001-T04", "**/api/v1/raw-source-locator?*", lambda data: data.pop("source_file"), None),
            ("F001-T05", "**/api/v1/raw-source-locator?*", lambda data: data.__setitem__("raw_line_number", "1"), None),
            ("F001-T06", "**/api/v1/raw-row?*", lambda data: data["fields"]["sensor_01"].__setitem__("parsed_value", "518.67"), None),
            ("F001-T07", "**/api/v1/raw-row?*", lambda data: data["fields"]["sensor_01"].__setitem__("parsed_value", True), None),
            ("F001-T08", "**/api/v1/raw-row?*", lambda data: data["fields"].pop("sensor_01"), None),
            ("F001-T09", "**/api/v1/sensor-series?*", lambda data: None, lambda body: body.replace('"value":518.67', '"value":1e309', 1)),
            ("F001-T19", "**/api/v1/raw-row?*", lambda data: data.__setitem__("unit_id", 2), None),
            ("F001-T20-trend", "**/api/v1/sensor-trend?*", lambda data: data.__setitem__("start_value", None), None),
            ("F001-T20-quality", "**/api/v1/data-quality?*", lambda data: data["structure"].__setitem__("actual_rows", "20631"), None),
        ]
        for scenario, pattern, mutate, transform in scenarios:
            with self.subTest(scenario=scenario):
                context, page, errors = self.new_fault_page(pattern, mutate, body_transform=transform)
                try:
                    self.assert_failed_closed(page, errors)
                    if scenario == "F001-T01":
                        path = EVIDENCE / "S10.png"
                        page.screenshot(path=str(path), full_page=True)
                        self.screenshots["S10"] = {"captured_at_utc": datetime.now(timezone.utc).isoformat(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "state": "Corrected M5-F-001 malformed-response fail-closed state", "file": path.name}
                finally:
                    context.close()

    def test_m5_07_f001_t10_legitimate_undefined_pearson(self) -> None:
        response = self.page.request.get(self.base + "/api/v1/sensor-trend?split=train&unit_id=1&sensor_id=sensor_01").json()["data"]
        self.assertIsNone(response["pearson_correlation"])
        self.assertEqual(self.statistics("#trend-stats")["Pearson r"], "UNDEFINED")
        prompt = self.prompt()
        self.assertIn("pearson_r=UNDEFINED", prompt)
        self.assertFalse(self.page.locator("#copy-prompt").is_disabled())
        self.assertNotRegex(self.page.locator("#trend-stats").inner_text(), r"\bNaN\b|Infinity|Pearson r\s+0(?:\.0+)?\b")
        self.capture("S05", "Legitimate constant-sensor Pearson null displayed as UNDEFINED")

    def test_m5_08_f001_t11_to_t14_fail_closed_and_recovery_clipboard(self) -> None:
        original = self.prompt()
        self.assertTrue(original)

        def malformed_row(route):
            response = route.fetch()
            payload = response.json()
            payload["data"]["fields"]["sensor_01"]["parsed_value"] = None
            route.fulfill(response=response, json=payload)

        self.page.route("**/api/v1/raw-row?*", malformed_row)
        self.page.select_option("#cycle-select", "2")
        self.page.locator("#error-panel[data-error-kind='malformed-response']").wait_for()
        self.assert_failed_closed(self.page, self.page_errors)
        self.page.unroute("**/api/v1/raw-row?*", malformed_row)
        self.page.select_option("#cycle-select", "3")
        self.ready()
        recovered = self.prompt()
        self.page.click("#copy-prompt")
        self.page.locator("#prompt-status", has_text="成功複製").wait_for()
        copied = self.page.evaluate("navigator.clipboard.readText()")
        self.assertEqual(copied.replace("\r\n", "\n"), recovered.replace("\r\n", "\n"))
        self.assertIn("selected_cycle=3", recovered)
        self.capture("S11", "Valid response recovery with regenerated and copied Evidence Prompt")

    def test_m5_09_f001_t15_delayed_malformed_isolation(self) -> None:
        self.context.add_init_script(script="""
            (() => { const nativeFetch = window.fetch.bind(window); window.fetch = async (input, init = {}) => {
              const url = typeof input === 'string' ? input : input.url; const detached = {...init}; delete detached.signal;
              const response = await nativeFetch(input, detached);
              if (url.includes('/raw-row?') && url.includes('cycle=2')) {
                const payload = await response.json(); payload.data.fields.sensor_02.parsed_value = null;
                await new Promise(resolve => setTimeout(resolve, 650)); document.documentElement.dataset.staleMalformedReleased = 'true';
                return new Response(JSON.stringify(payload), {status:200,headers:{'Content-Type':'application/json'}});
              }
              if (url.includes('sensor_03') || url.includes('cycle=3')) await new Promise(resolve => setTimeout(resolve, 20));
              return response;
            }; })();
        """)
        self.page.reload(wait_until="domcontentloaded")
        self.ready()
        self.page.select_option("#sensor-select", "sensor_02")
        self.page.select_option("#cycle-select", "2")
        self.page.select_option("#sensor-select", "sensor_03")
        self.page.select_option("#cycle-select", "3")
        self.ready()
        self.page.locator("html[data-stale-malformed-released='true']").wait_for()
        self.assertTrue(self.page.locator("#error-panel").is_hidden())
        self.assertIn("selected_cycle=3", self.prompt())

    def test_m5_10_f001_t16_t17_delayed_valid_and_current_malformed(self) -> None:
        self.context.add_init_script(script="""
            (() => { const nativeFetch = window.fetch.bind(window); window.fetch = async (input, init = {}) => {
              const url = typeof input === 'string' ? input : input.url; const detached = {...init}; delete detached.signal;
              const response = await nativeFetch(input, detached);
              if (url.includes('/raw-row?') && url.includes('cycle=2')) {
                await new Promise(resolve => setTimeout(resolve, 650)); document.documentElement.dataset.staleValidReleased = 'true'; return response;
              }
              if (url.includes('/raw-row?') && url.includes('cycle=3')) {
                const payload = await response.json(); payload.data.fields.sensor_01.parsed_value = null;
                return new Response(JSON.stringify(payload), {status:200,headers:{'Content-Type':'application/json'}});
              }
              return response;
            }; })();
        """)
        self.page.reload(wait_until="domcontentloaded")
        self.ready()
        self.page.select_option("#cycle-select", "2")
        self.page.select_option("#cycle-select", "3")
        self.page.locator("#error-panel[data-error-kind='malformed-response']").wait_for()
        self.page.locator("html[data-stale-valid-released='true']").wait_for()
        self.assert_failed_closed(self.page, self.page_errors)

    def test_m5_11_f001_t18_rul_validation_and_rul_semantics(self) -> None:
        def invalid_rul(route):
            response = route.fetch()
            payload = response.json()
            payload["data"]["rul_cycles"] = None
            route.fulfill(response=response, json=payload)

        self.page.route("**/api/v1/test-rul?*", invalid_rul)
        self.page.select_option("#split-select", "test")
        self.page.locator("#error-panel[data-error-kind='malformed-response']").wait_for()
        self.assert_failed_closed(self.page, self.page_errors)
        self.page.unroute("**/api/v1/test-rul?*", invalid_rul)
        self.page.select_option("#split-select", "train")
        self.ready()
        self.select("test", 100, 90, 110, 100, "sensor_02")
        expected = self.rul[99]
        self.assertEqual((expected["line"], expected["index"], expected["token"], expected["value"]), (100, 99, "20", 20))
        self.assertEqual(self.page.locator("#rul-value").inner_text(), "20 cycles")
        prompt = self.prompt()
        self.assertIn("test_rul_cycles: 20", prompt)
        self.assertIn("final observed cycle 198; not arbitrary Selected Cycle 100", prompt)
        self.select("train", 1, 90, 100, 96, "sensor_01")
        self.assertIn("train_rul: NOT_APPLICABLE", self.prompt())

    def test_m5_12_actual_server_interruption_recovery_and_final_workflow(self) -> None:
        secondary = create_server(port=0, project_root=ROOT)
        port = secondary.server_port
        thread = threading.Thread(target=secondary.serve_forever, daemon=True)
        thread.start()
        context = self.browser.new_context(viewport={"width": 1440, "height": 1100})
        origin = f"http://127.0.0.1:{port}"
        context.grant_permissions(["clipboard-read", "clipboard-write"], origin=origin)
        page = context.new_page()
        restarted = None
        restart_thread = None
        try:
            page.goto(origin, wait_until="domcontentloaded")
            page.locator("#ui-state", has_text="資料已就緒").wait_for()
            secondary.shutdown()
            secondary.server_close()
            thread.join(timeout=5)
            page.select_option("#cycle-select", "2")
            page.locator("#error-panel[data-error-kind='api-unavailable']").wait_for(timeout=15000)
            path = EVIDENCE / "S07.png"
            page.screenshot(path=str(path), full_page=True)
            self.screenshots["S07"] = {"captured_at_utc": datetime.now(timezone.utc).isoformat(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "state": "Actual loopback server unavailable", "file": path.name}
            self.assertTrue(page.locator("#copy-prompt").is_disabled())
            restarted = create_server(port=port, project_root=ROOT)
            restart_thread = threading.Thread(target=restarted.serve_forever, daemon=True)
            restart_thread.start()
            page.reload(wait_until="domcontentloaded")
            page.locator("#ui-state", has_text="資料已就緒").wait_for()
            page.select_option("#split-select", "test")
            page.locator("#ui-state", has_text="資料已就緒").wait_for()
            page.select_option("#unit-select", "100")
            page.locator("#ui-state", has_text="資料已就緒").wait_for()
            for selector, value in (("#start-cycle-select", "90"), ("#end-cycle-select", "110"), ("#cycle-select", "100"), ("#sensor-select", "sensor_02")):
                page.select_option(selector, value)
                page.locator("#ui-state", has_text="資料已就緒").wait_for()
            page.click("#generate-prompt")
            page.locator("#prompt-preview[data-valid='true']").wait_for()
            preview = page.locator("#prompt-preview").input_value()
            page.click("#copy-prompt")
            page.locator("#prompt-status", has_text="成功複製").wait_for()
            self.assertEqual(page.evaluate("navigator.clipboard.readText()").replace("\r\n", "\n"), preview.replace("\r\n", "\n"))
            path = EVIDENCE / "S08.png"
            page.screenshot(path=str(path), full_page=True)
            self.screenshots["S08"] = {"captured_at_utc": datetime.now(timezone.utc).isoformat(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "state": "Actual loopback service restored and final workflow valid", "file": path.name}
        finally:
            context.close()
            if restarted:
                restarted.shutdown()
                restarted.server_close()
            if restart_thread:
                restart_thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
