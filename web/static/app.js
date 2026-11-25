"use strict";

const $ = id => document.getElementById(id);
const selectors = {
  split: $("split-select"),
  unit: $("unit-select"),
  startCycle: $("start-cycle-select"),
  endCycle: $("end-cycle-select"),
  cycle: $("cycle-select"),
  sensor: $("sensor-select"),
};
let version = 0;
let controller = null;
let availableCycles = [];
let statusMetadata = null;
let loadedEvidence = null;
let generatedPromptKey = null;

function isCurrent(transaction) {
  return transaction.version === version && transaction.controller === controller;
}

function snapshotKey(snapshot) {
  return JSON.stringify(snapshot);
}

function promptState(message, kind = "invalid") {
  $("prompt-status").textContent = message;
  $("prompt-status").dataset.state = kind;
}

function invalidatePrompt(message = "選取已變更；請等待目前證據完成載入。") {
  loadedEvidence = null;
  generatedPromptKey = null;
  $("prompt-preview").value = "";
  $("prompt-preview").dataset.valid = "false";
  $("generate-prompt").disabled = true;
  $("copy-prompt").disabled = true;
  promptState(message);
}

function resetCycleSelectors() {
  availableCycles = [];
  for (const select of [selectors.startCycle, selectors.endCycle, selectors.cycle]) {
    select.replaceChildren();
    select.disabled = true;
  }
}

function beginTransition(message, reset = "none") {
  version += 1;
  if (controller) controller.abort();
  controller = new AbortController();
  const transaction = {version, controller, signal: controller.signal};
  invalidatePrompt();
  if (reset === "units") {
    selectors.unit.replaceChildren();
    selectors.unit.disabled = true;
    resetCycleSelectors();
  } else if (reset === "cycles") {
    resetCycleSelectors();
  }
  clearView();
  state(message, "loading");
  return transaction;
}

function fmt(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "UNDEFINED";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : Number(value.toPrecision(8)).toString();
  return String(value);
}

async function api(path, transaction) {
  const response = await fetch(path, {signal: transaction.signal, headers: {Accept: "application/json"}});
  const payload = await response.json();
  if (!payload.ok) {
    const error = new Error(payload.error.message);
    error.code = payload.error.code;
    throw error;
  }
  return payload.data;
}

function setOptions(select, items, label = item => item) {
  select.replaceChildren(...items.map(item => {
    const option = document.createElement("option");
    option.value = String(item);
    option.textContent = label(item);
    return option;
  }));
  select.disabled = items.length === 0;
}

function state(text, kind = "ready") {
  $("ui-state").textContent = text;
  $("ui-state").dataset.state = kind;
  $("error-panel").classList.add("hidden");
  $("status-card").classList.toggle("failure", kind === "error");
  $("status-card").classList.toggle("ready", kind === "ready");
}

function clearView() {
  $("selected-value").textContent = "—";
  $("selected-sensor").textContent = "—";
  $("chart-title").textContent = "趨勢圖";
  $("range-badge").textContent = "—";
  for (const id of ["trend-chart", "trend-stats", "range-stats", "selection-summary", "op-settings", "field-table", "locator-detail", "quality-summary", "quality-limitations"]) {
    $(id).replaceChildren();
  }
  $("quality-gate").textContent = "—";
  $("rul-value").textContent = "—";
  $("rul-panel").classList.add("hidden");
  document.querySelector("main").setAttribute("aria-busy", "true");
}

function errorKind(error) {
  if (error.code === "SOURCE_INTEGRITY_FAILURE") return "source-integrity";
  if (error.code === "EMPTY_QUERY_RESULT") return "empty-result";
  if (["INVALID_REQUEST", "INVALID_SPLIT", "INVALID_CYCLE", "UNKNOWN_UNIT", "UNKNOWN_SENSOR"].includes(error.code)) return "invalid-selection";
  if (!error.code || error instanceof TypeError) return "api-unavailable";
  return "api-error";
}

function fail(error, transaction) {
  if (!isCurrent(transaction) || error.name === "AbortError") return;
  invalidatePrompt("資料載入失敗；提示詞不可產生或複製。");
  const kind = errorKind(error);
  $("error-panel").textContent = `${error.code || "API_UNAVAILABLE"}: ${error.message}`;
  $("error-panel").dataset.errorKind = kind;
  state(`資料無法載入（${kind}）`, "error");
  $("error-panel").classList.remove("hidden");
  document.querySelector("main").setAttribute("aria-busy", "false");
}

function dl(target, data) {
  target.replaceChildren();
  Object.entries(data).forEach(([key, value]) => {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = key;
    dd.textContent = fmt(value);
    target.append(dt, dd);
  });
}

function statBoxes(target, values) {
  target.replaceChildren(...Object.entries(values).map(([key, value]) => {
    const box = document.createElement("div");
    const label = document.createElement("span");
    const strong = document.createElement("strong");
    box.className = "stat";
    label.textContent = key;
    strong.textContent = fmt(value);
    box.append(label, strong);
    return box;
  }));
}

function rangeStatistics(points) {
  if (!points.length) return null;
  const values = points.map(point => point.value);
  return {
    cycle_start: points[0].cycle,
    cycle_end: points.at(-1).cycle,
    sample_count: points.length,
    start_value: values[0],
    end_value: values.at(-1),
    change: values.at(-1) - values[0],
    minimum: Math.min(...values),
    maximum: Math.max(...values),
    mean: values.reduce((sum, value) => sum + value, 0) / values.length,
  };
}

function renderStatistics(trend, selectedRange) {
  statBoxes($("trend-stats"), {
    Start: trend.start_value,
    End: trend.end_value,
    Change: trend.change,
    "OLS slope": trend.slope,
    "Pearson r": trend.pearson_correlation,
    Direction: trend.direction,
    Samples: trend.sample_count,
    "Cycle range": `${trend.cycle_start}–${trend.cycle_end}`,
  });
  statBoxes($("range-stats"), {
    Start: selectedRange.start_value,
    End: selectedRange.end_value,
    Change: selectedRange.change,
    Minimum: selectedRange.minimum,
    Maximum: selectedRange.maximum,
    Mean: selectedRange.mean,
    Samples: selectedRange.sample_count,
    "Actual range": `${selectedRange.cycle_start}–${selectedRange.cycle_end}`,
  });
}

function chart(series, selectedCycle) {
  const svg = $("trend-chart");
  const points = series.points;
  const width = 900;
  const height = 350;
  const pad = {l: 68, r: 28, t: 24, b: 48};
  svg.replaceChildren();
  if (!points.length) return;
  const minX = points[0].cycle;
  const maxX = points.at(-1).cycle;
  let minY = Math.min(...points.map(point => point.value));
  let maxY = Math.max(...points.map(point => point.value));
  if (minY === maxY) {
    const margin = Math.max(Math.abs(minY) * 0.01, 1);
    minY -= margin;
    maxY += margin;
  }
  const x = value => pad.l + (value - minX) / Math.max(1, maxX - minX) * (width - pad.l - pad.r);
  const y = value => pad.t + (maxY - value) / (maxY - minY) * (height - pad.t - pad.b);
  const ns = "http://www.w3.org/2000/svg";
  for (let index = 0; index < 5; index += 1) {
    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", pad.l);
    line.setAttribute("x2", width - pad.r);
    line.setAttribute("y1", pad.t + index * (height - pad.t - pad.b) / 4);
    line.setAttribute("y2", pad.t + index * (height - pad.t - pad.b) / 4);
    line.setAttribute("class", "chart-grid");
    svg.append(line);
  }
  const path = document.createElementNS(ns, "path");
  path.setAttribute("d", points.map((point, index) => `${index ? "L" : "M"}${x(point.cycle).toFixed(2)},${y(point.value).toFixed(2)}`).join(" "));
  path.setAttribute("class", "chart-line");
  svg.append(path);
  const selected = points.find(point => point.cycle === selectedCycle);
  if (selected) {
    const dot = document.createElementNS(ns, "circle");
    dot.setAttribute("cx", x(selected.cycle));
    dot.setAttribute("cy", y(selected.value));
    dot.setAttribute("r", 7);
    dot.setAttribute("class", "chart-dot");
    svg.append(dot);
  }
  [[pad.l, height - 16, `Cycle ${minX}`], [width - pad.r - 85, height - 16, `Cycle ${maxX}`], [8, pad.t + 5, fmt(maxY)], [8, height - pad.b, fmt(minY)]].forEach(([xx, yy, text]) => {
    const label = document.createElementNS(ns, "text");
    label.setAttribute("x", xx);
    label.setAttribute("y", yy);
    label.setAttribute("class", "axis-label");
    label.textContent = text;
    svg.append(label);
  });
}

function renderFields(row, sensor) {
  $("field-table").replaceChildren(...Object.values(row.fields).map(field => {
    const tr = document.createElement("tr");
    if (field.canonical_field_name === sensor) tr.className = "selected";
    [field.raw_column_index, field.canonical_field_name, field.raw_value, fmt(field.parsed_value)].forEach(value => {
      const td = document.createElement("td");
      td.textContent = value;
      tr.append(td);
    });
    return tr;
  }));
}

function renderQuality(data) {
  $("quality-gate").textContent = data.quality_gate;
  const quality = data.quality;
  const structure = data.structure;
  const items = {
    Structure: structure.passed ? "PASS" : "FAIL",
    Rows: structure.actual_rows,
    Units: structure.unit_count,
    Duplicates: quality.duplicate_full_rows,
    Missing: quality.missing_values,
    "Cycle gaps": quality.missing_cycle_units,
    "Constant fields": Object.values(quality.feature_statistics).filter(item => item.constant).length,
    "Near constant": Object.values(quality.feature_statistics).filter(item => item.near_constant).length,
    "Potential outliers": Object.values(quality.feature_statistics).reduce((sum, item) => sum + item.potential_outlier_count, 0),
    "Source SHA": `${data.source_sha256.slice(0, 12)}…`,
  };
  $("quality-summary").replaceChildren(...Object.entries(items).map(([key, value]) => {
    const div = document.createElement("div");
    const label = document.createElement("span");
    const strong = document.createElement("strong");
    div.className = "quality-item";
    label.textContent = key;
    strong.textContent = value;
    div.append(label, strong);
    return div;
  }));
  $("quality-limitations").replaceChildren(...data.limitations.map(text => {
    const paragraph = document.createElement("p");
    paragraph.textContent = `• ${text}`;
    return paragraph;
  }));
}

function selectionSnapshot() {
  const snapshot = {
    split: selectors.split.value,
    unit: Number(selectors.unit.value),
    startCycle: Number(selectors.startCycle.value),
    endCycle: Number(selectors.endCycle.value),
    cycle: Number(selectors.cycle.value),
    sensor: selectors.sensor.value,
  };
  const integerFields = [snapshot.unit, snapshot.startCycle, snapshot.endCycle, snapshot.cycle];
  if (!snapshot.split || !snapshot.sensor || integerFields.some(value => !Number.isInteger(value) || value <= 0)) {
    const error = new Error("The current selection is incomplete.");
    error.code = "INVALID_REQUEST";
    throw error;
  }
  if (snapshot.startCycle > snapshot.endCycle || snapshot.cycle < snapshot.startCycle || snapshot.cycle > snapshot.endCycle) {
    const error = new Error("Start Cycle, End Cycle and Selected Cycle are inconsistent.");
    error.code = "INVALID_CYCLE";
    throw error;
  }
  return snapshot;
}

function filteredPoints(series, selected) {
  return series.points.filter(point => point.cycle >= selected.startCycle && point.cycle <= selected.endCycle);
}

function buildPrompt(evidence) {
  const {selected, row, trend, selectedRange, ops, quality, locator, rul, series} = evidence;
  const field = row.fields[selected.sensor];
  const qualityScope = `${quality.dataset_split} dataset (${quality.structure.actual_rows} rows, ${quality.structure.unit_count} units)`;
  const rulLines = selected.split === "test"
    ? [`test_rul_cycles: ${rul.rul_cycles}`, `test_rul_observation_basis: Test Unit ${selected.unit} final observed cycle ${series.cycle_end}; not arbitrary Selected Cycle ${selected.cycle}`]
    : ["train_rul: NOT_APPLICABLE (RUL_FD001.txt supplies Test Units only)"];
  return [
    "OBSERVED_DATA",
    `dataset_identity: ${statusMetadata.dataset_id}`,
    `source_policy: ${statusMetadata.source_trust_policy}; external_source_verification=${statusMetadata.external_source_verification}`,
    `selection: split=${selected.split}, unit=${selected.unit}, start_cycle=${selected.startCycle}, end_cycle=${selected.endCycle}, selected_cycle=${selected.cycle}, sensor=${selected.sensor}`,
    `selected_observation: raw_token=${field.raw_value}; parsed_value=${fmt(field.parsed_value)}`,
    `operational_settings: op_setting_1=${fmt(ops.op_setting_1)}, op_setting_2=${fmt(ops.op_setting_2)}, op_setting_3=${fmt(ops.op_setting_3)}`,
    `raw_source_locator: source_file=${locator.source_file}; source_sha256=${locator.source_sha256}; raw_line_number=${locator.raw_line_number}; parsed_row_index=${locator.parsed_row_index}; raw_column_index=${locator.raw_column_index}; canonical_field=${locator.canonical_field_name}; raw_token=${locator.raw_value}; parsed_value=${fmt(locator.parsed_value)}`,
    ...rulLines,
    "",
    "DERIVED_STATISTICS",
    `displayed_range: actual_cycle_start=${selectedRange.cycle_start}; actual_cycle_end=${selectedRange.cycle_end}; sample_count=${selectedRange.sample_count}`,
    `FULL_UNIT_STATISTICS: cycle_range=${trend.cycle_start}-${trend.cycle_end}; sample_count=${trend.sample_count}; start_value=${fmt(trend.start_value)}; end_value=${fmt(trend.end_value)}; change=${fmt(trend.change)}; ols_slope=${fmt(trend.slope)}; pearson_r=${fmt(trend.pearson_correlation)}; direction=${trend.direction}`,
    `SELECTED_RANGE_STATISTICS: cycle_range=${selectedRange.cycle_start}-${selectedRange.cycle_end}; sample_count=${selectedRange.sample_count}; start_value=${fmt(selectedRange.start_value)}; end_value=${fmt(selectedRange.end_value)}; change=${fmt(selectedRange.change)}; minimum=${fmt(selectedRange.minimum)}; maximum=${fmt(selectedRange.maximum)}; arithmetic_mean=${fmt(selectedRange.mean)}`,
    `data_quality: scope=${qualityScope}; gate=${quality.quality_gate}; missing_values=${quality.quality.missing_values}; duplicate_full_rows=${quality.quality.duplicate_full_rows}; missing_cycle_units=${quality.quality.missing_cycle_units}`,
    "",
    "ANALYSIS_QUESTIONS",
    "- What descriptive trend is supported by the displayed observations?",
    "- Is the series constant, variable, or statistically limited?",
    "- Which observed values and source locators support the analysis?",
    "- Which conclusions require additional evidence?",
    "",
    "LIMITATIONS",
    "- STUDENT_TRUSTED_LOCAL_FILES does not equal independent NASA official-source verification.",
    "- Sensor physical names and units are UNVERIFIED.",
    "- Descriptive trend does not establish causality.",
    "- These observations do not confirm a fault cause or diagnosis.",
    "- Do not infer an unvalidated RUL prediction.",
    "- Train RUL is not applicable.",
    "- Test RUL corresponds only to the Test Unit final observed cycle, not an arbitrary Selected Cycle.",
    "- Do not generalize a single observation or selected range to every engine.",
  ].join("\n");
}

function evidenceStillCurrent(evidence) {
  if (!evidence || evidence.version !== version) return false;
  try {
    return snapshotKey(selectionSnapshot()) === snapshotKey(evidence.selected);
  } catch (_) {
    return false;
  }
}

function generatePrompt() {
  if (!evidenceStillCurrent(loadedEvidence)) {
    invalidatePrompt("目前選取與已載入證據不一致；無法產生提示詞。");
    return;
  }
  const prompt = buildPrompt(loadedEvidence);
  $("prompt-preview").value = prompt;
  $("prompt-preview").dataset.valid = "true";
  generatedPromptKey = snapshotKey(loadedEvidence.selected);
  $("copy-prompt").disabled = false;
  promptState("提示詞已由目前有效 selection snapshot 產生。", "success");
}

async function copyPrompt() {
  const key = generatedPromptKey;
  const text = $("prompt-preview").value;
  if (!text || $("prompt-preview").dataset.valid !== "true" || !evidenceStillCurrent(loadedEvidence) || key !== snapshotKey(loadedEvidence.selected)) {
    $("copy-prompt").disabled = true;
    promptState("提示詞已失效，禁止複製；請重新產生。", "error");
    return;
  }
  try {
    await navigator.clipboard.writeText(text);
    if (!evidenceStillCurrent(loadedEvidence) || key !== generatedPromptKey) {
      promptState("複製期間選取已變更；舊提示詞已失效。", "error");
      return;
    }
    promptState("提示詞已成功複製到剪貼簿。", "success");
  } catch (_) {
    promptState("無法存取剪貼簿；預覽內容仍可手動選取。", "error");
  }
}

async function refresh(transaction) {
  const selected = selectionSnapshot();
  const base = `split=${selected.split}&unit_id=${selected.unit}`;
  const [row, trend, series, ops, quality, locator, rul] = await Promise.all([
    api(`/api/v1/raw-row?${base}&cycle=${selected.cycle}`, transaction),
    api(`/api/v1/sensor-trend?${base}&sensor_id=${selected.sensor}`, transaction),
    api(`/api/v1/sensor-series?${base}&sensor_id=${selected.sensor}`, transaction),
    api(`/api/v1/operational-settings?${base}&cycle=${selected.cycle}`, transaction),
    api(`/api/v1/data-quality?split=${selected.split}`, transaction),
    api(`/api/v1/raw-source-locator?${base}&cycle=${selected.cycle}&field_name=${selected.sensor}`, transaction),
    selected.split === "test" ? api(`/api/v1/test-rul?${base}`, transaction) : Promise.resolve(null),
  ]);
  if (!isCurrent(transaction) || snapshotKey(selectionSnapshot()) !== snapshotKey(selected)) return;
  const points = filteredPoints(series, selected);
  if (!points.length) {
    const error = new Error("No actual observations exist in the selected range.");
    error.code = "EMPTY_QUERY_RESULT";
    throw error;
  }
  const selectedRange = rangeStatistics(points);
  const displayedSeries = {...series, cycle_start: points[0].cycle, cycle_end: points.at(-1).cycle, sample_count: points.length, points};
  $("selected-value").textContent = fmt(row.fields[selected.sensor].parsed_value);
  $("selected-sensor").textContent = selected.sensor;
  $("chart-title").textContent = `${selected.sensor} · Unit ${selected.unit}`;
  $("range-badge").textContent = `Cycle ${displayedSeries.cycle_start}–${displayedSeries.cycle_end} · ${displayedSeries.sample_count} samples`;
  dl($("selection-summary"), {"Dataset Split": selected.split.toUpperCase(), "Engine Unit": selected.unit, "Start Cycle": selected.startCycle, "End Cycle": selected.endCycle, Cycle: selected.cycle, "Selected Sensor": selected.sensor});
  $("op-settings").replaceChildren(...[1, 2, 3].map(index => {
    const div = document.createElement("div");
    const label = document.createElement("small");
    const value = document.createElement("strong");
    label.textContent = `Setting ${index}`;
    value.textContent = fmt(ops[`op_setting_${index}`]);
    div.append(label, value);
    return div;
  }));
  renderFields(row, selected.sensor);
  dl($("locator-detail"), locator);
  renderStatistics(trend, selectedRange);
  chart(displayedSeries, selected.cycle);
  renderQuality(quality);
  $("rul-panel").classList.toggle("hidden", !rul);
  if (rul) $("rul-value").textContent = `${rul.rul_cycles} cycles`;
  loadedEvidence = {version: transaction.version, selected, row, trend, series, displayedSeries, selectedRange, ops, quality, locator, rul};
  $("generate-prompt").disabled = false;
  promptState("目前證據已就緒；可產生提示詞。", "ready");
  document.querySelector("main").setAttribute("aria-busy", "false");
  state("資料已就緒");
}

function rebuildSelectedCycleOptions(preferred) {
  const start = Number(selectors.startCycle.value);
  const end = Number(selectors.endCycle.value);
  const valid = availableCycles.filter(cycle => cycle >= start && cycle <= end);
  setOptions(selectors.cycle, valid);
  if (valid.includes(preferred)) selectors.cycle.value = String(preferred);
  else if (valid.length) selectors.cycle.value = String(preferred < start ? valid[0] : valid.at(-1));
}

function normalizeRange(changed) {
  let start = Number(selectors.startCycle.value);
  let end = Number(selectors.endCycle.value);
  const selected = Number(selectors.cycle.value);
  if (start > end) {
    if (changed === "start") {
      selectors.endCycle.value = String(start);
      end = start;
    } else {
      selectors.startCycle.value = String(end);
      start = end;
    }
  }
  rebuildSelectedCycleOptions(selected);
  return {start, end};
}

async function loadCycles(transaction, split, unit) {
  const data = await api(`/api/v1/cycles?split=${split}&unit_id=${unit}`, transaction);
  if (!isCurrent(transaction) || selectors.split.value !== split || Number(selectors.unit.value) !== unit) return;
  if (!data.cycles.length) {
    const error = new Error("No cycles are available for the selected Unit.");
    error.code = "EMPTY_QUERY_RESULT";
    throw error;
  }
  availableCycles = data.cycles.slice();
  setOptions(selectors.startCycle, availableCycles);
  setOptions(selectors.endCycle, availableCycles);
  selectors.endCycle.value = String(availableCycles.at(-1));
  setOptions(selectors.cycle, availableCycles);
  await refresh(transaction);
}

async function loadUnits(transaction, split) {
  const data = await api(`/api/v1/units?split=${split}`, transaction);
  if (!isCurrent(transaction) || selectors.split.value !== split) return;
  if (!data.units.length) {
    const error = new Error("No Units are available for the selected Split.");
    error.code = "EMPTY_QUERY_RESULT";
    throw error;
  }
  setOptions(selectors.unit, data.units);
  await loadCycles(transaction, split, Number(selectors.unit.value));
}

async function init() {
  const transaction = beginTransition("正在驗證本地資料…", "units");
  try {
    const [statusData, splitData, sensorData] = await Promise.all([
      api("/api/v1/status", transaction),
      api("/api/v1/splits", transaction),
      api("/api/v1/sensors", transaction),
    ]);
    if (!isCurrent(transaction)) return;
    if (!statusData.data_available) {
      const error = new Error("Validated FD001 data is unavailable.");
      error.code = "SOURCE_INTEGRITY_FAILURE";
      throw error;
    }
    statusMetadata = statusData;
    $("validation-status").textContent = statusData.validation_status;
    $("dataset-id").textContent = statusData.dataset_id;
    $("contract-version").textContent = `Data Contract v${statusData.contract_version} · ${statusData.source_trust_policy}`;
    setOptions(selectors.split, splitData.dataset_splits, item => item.toUpperCase());
    setOptions(selectors.sensor, sensorData.sensors.map(item => item.sensor_id));
    await loadUnits(transaction, selectors.split.value);
  } catch (error) {
    fail(error, transaction);
  }
}

selectors.split.addEventListener("change", () => {
  const transaction = beginTransition("更新 Dataset Split…", "units");
  loadUnits(transaction, selectors.split.value).catch(error => fail(error, transaction));
});
selectors.unit.addEventListener("change", () => {
  const split = selectors.split.value;
  const unit = Number(selectors.unit.value);
  const transaction = beginTransition("更新 Engine Unit 與 Cycle…", "cycles");
  loadCycles(transaction, split, unit).catch(error => fail(error, transaction));
});
selectors.startCycle.addEventListener("change", () => {
  normalizeRange("start");
  const transaction = beginTransition("更新 Cycle 範圍…");
  refresh(transaction).catch(error => fail(error, transaction));
});
selectors.endCycle.addEventListener("change", () => {
  normalizeRange("end");
  const transaction = beginTransition("更新 Cycle 範圍…");
  refresh(transaction).catch(error => fail(error, transaction));
});
for (const selector of [selectors.cycle, selectors.sensor]) {
  selector.addEventListener("change", () => {
    const transaction = beginTransition("更新所選資料…");
    refresh(transaction).catch(error => fail(error, transaction));
  });
}
$("generate-prompt").addEventListener("click", generatePrompt);
$("copy-prompt").addEventListener("click", copyPrompt);

init();
