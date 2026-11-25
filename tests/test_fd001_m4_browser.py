from __future__ import annotations

import hashlib
import json
import math
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
CONTRACT = json.loads((ROOT / "contracts" / "FD001_DATA_CONTRACT.json").read_text(encoding="utf-8"))
CONTRACT_IDENTITY = {item["dataset_split"]: item for item in CONTRACT["dataset_identity"]}
PROMPT_SECTIONS = {"OBSERVED_DATA", "DERIVED_STATISTICS", "ANALYSIS_QUESTIONS", "LIMITATIONS"}


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


def raw_rul_rows() -> list[dict[str, object]]:
    """Independent RUL oracle preserving raw and effective-row indices."""
    rows: list[dict[str, object]] = []
    effective_index = 0
    for line_number, line in enumerate((DATA / "RUL_FD001.txt").read_text(encoding="ascii").splitlines(), start=1):
        tokens = line.split()
        if not tokens:
            continue
        rows.append({
            "line": line_number,
            "effective_index": effective_index,
            "raw_token": tokens[0],
            "value": int(float(tokens[0])),
        })
        effective_index += 1
    return rows


class FD001M4BrowserUAT(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not EDGE.is_file():
            raise RuntimeError("Microsoft Edge browser executable is unavailable.")
        SCREENSHOTS.mkdir(parents=True, exist_ok=True)
        cls.raw = {split: raw_rows(split) for split in ("train", "test")}
        cls.raw_rul = raw_rul_rows()
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

    def definition_list(self, selector: str) -> dict[str, str]:
        keys = self.page.locator(f"{selector} dt").all_text_contents()
        values = self.page.locator(f"{selector} dd").all_text_contents()
        self.assertEqual(len(keys), len(values))
        self.assertEqual(len(keys), len(set(keys)), f"Duplicate DOM field names in {selector}")
        return dict(zip(keys, values))

    def statistic_fields(self, selector: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for item in self.page.locator(f"{selector} .stat").all():
            name = item.locator("span").inner_text()
            self.assertNotIn(name, fields, f"Duplicate statistic field: {name}")
            fields[name] = item.locator("strong").inner_text()
        return fields

    @staticmethod
    def prompt_sections(prompt: str) -> dict[str, list[str]]:
        sections = {name: [] for name in PROMPT_SECTIONS}
        active: str | None = None
        for line in prompt.replace("\r\n", "\n").splitlines():
            if line in PROMPT_SECTIONS:
                active = line
            elif active and line:
                sections[active].append(line)
        return sections

    def prompt_line(self, sections: dict[str, list[str]], section: str, prefix: str) -> str:
        matches = [line for line in sections[section] if line.startswith(prefix)]
        self.assertEqual(len(matches), 1, f"Expected exactly one {prefix!r} field in {section}")
        return matches[0][len(prefix):]

    @staticmethod
    def key_values(text: str, separator: str = "; ") -> dict[str, str]:
        fields: dict[str, str] = {}
        for item in text.split(separator):
            key, value = item.split("=", 1)
            if key in fields:
                raise AssertionError(f"Duplicate prompt field: {key}")
            fields[key] = value
        return fields

    def assert_derived_display(self, actual: str, expected: float, label: str) -> None:
        """Production fmt uses eight significant digits for non-integers."""
        if expected == 0:
            tolerance = 5.1e-9
        else:
            tolerance = 0.51 * 10 ** (math.floor(math.log10(abs(expected))) - 7)
        self.assertAlmostEqual(float(actual), expected, delta=tolerance, msg=f"{label}; tolerance={tolerance}")

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

    def assert_case(self, split: str, unit: int, sensor: str, column: int, start: int, end: int, cycle: int, screenshot: str | None) -> None:
        self.select_range(split, unit, start, end, cycle, sensor)
        full_unit_rows = self.unit_rows(split, unit)
        raw_range = [row for row in full_unit_rows if start <= row["cycle"] <= end]
        selected = next(row for row in raw_range if row["cycle"] == cycle)
        raw_values = [row["values"][column] for row in raw_range]
        expected_range = {
            "sample_count": len(raw_range),
            "cycle_start": raw_range[0]["cycle"],
            "cycle_end": raw_range[-1]["cycle"],
            "start_value": raw_values[0],
            "end_value": raw_values[-1],
            "change": raw_values[-1] - raw_values[0],
            "minimum": min(raw_values),
            "maximum": max(raw_values),
            "mean": sum(raw_values) / len(raw_values),
        }
        source_path = DATA / f"{split}_FD001.txt"
        source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
        identity = CONTRACT_IDENTITY[split]
        self.assertEqual(source_sha, identity["source_sha256"])

        # Retained raw-to-API point/order/token comparisons.
        api_series = self.page.request.get(self.base + f"/api/v1/sensor-series?split={split}&unit_id={unit}&sensor_id={sensor}").json()["data"]
        api_points = [point for point in api_series["points"] if start <= point["cycle"] <= end]
        self.assertEqual(len(api_points), len(raw_range))
        for raw, point in zip(raw_range, api_points):
            self.assertEqual(point["cycle"], raw["cycle"])
            self.assertEqual(point["value"], raw["values"][column])
            self.assertEqual(point["raw_value"], raw["tokens"][column])
        self.assertEqual(float(self.page.locator("#selected-value").inner_text()), selected["values"][column])

        # Exact DOM locator name/value mapping; no substring evidence.
        locator = self.definition_list("#locator-detail")
        expected_locator = {
            "dataset_id": identity["dataset_id"],
            "dataset_split": split,
            "source_file": identity["source_file"],
            "source_sha256": source_sha,
            "raw_line_number": str(selected["line"]),
            "parsed_row_index": str(selected["index"]),
            "unit_id": str(unit),
            "cycle": str(cycle),
            "raw_column_index": str(column + 1),
            "canonical_field_name": sensor,
            "raw_value": selected["tokens"][column],
            "parsed_value": str(selected["values"][column]),
        }
        self.assertEqual(locator, expected_locator)

        # Independently calculated range statistics versus named DOM fields.
        dom_range = self.statistic_fields("#range-stats")
        self.assertEqual(set(dom_range), {"Start", "End", "Change", "Minimum", "Maximum", "Mean", "Samples", "Actual range"})
        self.assertEqual(int(dom_range["Samples"]), expected_range["sample_count"])
        self.assertEqual(dom_range["Actual range"], f"{expected_range['cycle_start']}–{expected_range['cycle_end']}")
        for dom_name, expected_name in (("Start", "start_value"), ("End", "end_value"), ("Change", "change"), ("Minimum", "minimum"), ("Maximum", "maximum"), ("Mean", "mean")):
            self.assert_derived_display(dom_range[dom_name], expected_range[expected_name], f"DOM {dom_name}")

        # Full-unit/range scope separation from independent complete Unit rows.
        dom_full = self.statistic_fields("#trend-stats")
        self.assertEqual(int(dom_full["Samples"]), len(full_unit_rows))
        self.assertEqual(dom_full["Cycle range"], f"{full_unit_rows[0]['cycle']}–{full_unit_rows[-1]['cycle']}")
        self.assertNotEqual((len(full_unit_rows), full_unit_rows[-1]["cycle"]), (len(raw_range), raw_range[-1]["cycle"]))
        if len(set(row["values"][column] for row in full_unit_rows)) == 1:
            self.assertEqual(dom_full["Pearson r"], "UNDEFINED")

        # Retained independent SVG path and selected-dot comparisons.
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

        # Parse the prompt into exact sections and named fields.
        prompt = self.prompt()
        sections = self.prompt_sections(prompt)
        observed = sections["OBSERVED_DATA"]
        derived = sections["DERIVED_STATISTICS"]
        self.assertEqual(self.prompt_line(sections, "OBSERVED_DATA", "dataset_identity: "), identity["dataset_id"])
        source_policy = self.prompt_line(sections, "OBSERVED_DATA", "source_policy: ").split("; ")
        self.assertEqual(source_policy, [identity["source_trust_policy"], f"external_source_verification={identity['external_source_verification']}"])
        selection = self.key_values(self.prompt_line(sections, "OBSERVED_DATA", "selection: "), ", ")
        self.assertEqual(selection, {"split": split, "unit": str(unit), "start_cycle": str(start), "end_cycle": str(end), "selected_cycle": str(cycle), "sensor": sensor})
        observation = self.key_values(self.prompt_line(sections, "OBSERVED_DATA", "selected_observation: "))
        self.assertEqual(observation["raw_token"], selected["tokens"][column])
        self.assertEqual(float(observation["parsed_value"]), selected["values"][column])
        operations = self.key_values(self.prompt_line(sections, "OBSERVED_DATA", "operational_settings: "), ", ")
        for index in range(1, 4):
            self.assertEqual(float(operations[f"op_setting_{index}"]), selected["values"][index + 1])
        prompt_locator = self.key_values(self.prompt_line(sections, "OBSERVED_DATA", "raw_source_locator: "))
        self.assertEqual(prompt_locator, {
            "source_file": identity["source_file"],
            "source_sha256": source_sha,
            "raw_line_number": str(selected["line"]),
            "parsed_row_index": str(selected["index"]),
            "raw_column_index": str(column + 1),
            "canonical_field": sensor,
            "raw_token": selected["tokens"][column],
            "parsed_value": str(selected["values"][column]),
        })

        displayed = self.key_values(self.prompt_line(sections, "DERIVED_STATISTICS", "displayed_range: "))
        self.assertEqual(displayed, {"actual_cycle_start": str(start), "actual_cycle_end": str(end), "sample_count": str(len(raw_range))})
        prompt_full = self.key_values(self.prompt_line(sections, "DERIVED_STATISTICS", "FULL_UNIT_STATISTICS: "))
        self.assertEqual(prompt_full["cycle_range"], f"{full_unit_rows[0]['cycle']}-{full_unit_rows[-1]['cycle']}")
        self.assertEqual(int(prompt_full["sample_count"]), len(full_unit_rows))
        if len(set(row["values"][column] for row in full_unit_rows)) == 1:
            self.assertEqual(prompt_full["pearson_r"], "UNDEFINED")
        prompt_range = self.key_values(self.prompt_line(sections, "DERIVED_STATISTICS", "SELECTED_RANGE_STATISTICS: "))
        self.assertEqual(prompt_range["cycle_range"], f"{start}-{end}")
        self.assertEqual(int(prompt_range["sample_count"]), len(raw_range))
        for prompt_name, expected_name in (("start_value", "start_value"), ("end_value", "end_value"), ("change", "change"), ("minimum", "minimum"), ("maximum", "maximum"), ("arithmetic_mean", "mean")):
            self.assert_derived_display(prompt_range[prompt_name], expected_range[expected_name], f"Prompt {prompt_name}")

        if split == "test":
            rul = self.raw_rul[unit - 1]
            self.assertEqual(rul["line"], unit)
            self.assertEqual(rul["effective_index"], unit - 1)
            self.assertEqual(rul["raw_token"], str(rul["value"]))
            self.assertEqual(int(self.prompt_line(sections, "OBSERVED_DATA", "test_rul_cycles: ")), rul["value"])
            self.assertEqual(self.page.locator("#rul-value").inner_text(), f"{rul['value']} cycles")
            basis = self.prompt_line(sections, "OBSERVED_DATA", "test_rul_observation_basis: ")
            match = re.fullmatch(r"Test Unit (\d+) final observed cycle (\d+); not arbitrary Selected Cycle (\d+)", basis)
            self.assertIsNotNone(match)
            self.assertEqual(tuple(map(int, match.groups())), (unit, full_unit_rows[-1]["cycle"], cycle))
            self.assertNotEqual(full_unit_rows[-1]["cycle"], cycle)
            self.assertNotEqual(full_unit_rows[-1]["cycle"], end)
        else:
            self.assertFalse(self.page.locator("#rul-panel").is_visible())
            self.assertEqual(self.prompt_line(sections, "OBSERVED_DATA", "train_rul: "), "NOT_APPLICABLE (RUL_FD001.txt supplies Test Units only)")
            self.assertFalse(any(line.startswith("test_rul_cycles:") for line in observed))

        if screenshot:
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
        self.assert_case("train", 1, "sensor_01", 5, 96, 96, 96, None)
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
