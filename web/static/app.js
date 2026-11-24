"use strict";

const $ = id => document.getElementById(id);
const selectors = {
  split: $("split-select"), unit: $("unit-select"),
  cycle: $("cycle-select"), sensor: $("sensor-select"),
};
let version = 0;
let controller = null;

function isCurrent(transaction) {
  return transaction.version === version && transaction.controller === controller;
}

function beginTransition(message, reset = "none") {
  version += 1;
  if (controller) controller.abort();
  controller = new AbortController();
  const transaction = {version, controller, signal: controller.signal};
  if (reset === "units") {
    selectors.unit.replaceChildren(); selectors.unit.disabled = true;
    selectors.cycle.replaceChildren(); selectors.cycle.disabled = true;
  } else if (reset === "cycles") {
    selectors.cycle.replaceChildren(); selectors.cycle.disabled = true;
  }
  clearView();
  state(message, "loading");
  return transaction;
}

function fmt(value) {
  if (value === null || value === undefined) return "UNDEFINED";
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
    option.value = String(item); option.textContent = label(item);
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
  $("selected-value").textContent = "—"; $("selected-sensor").textContent = "—";
  $("chart-title").textContent = "趨勢圖"; $("range-badge").textContent = "—";
  for (const id of ["trend-chart", "trend-stats", "selection-summary", "op-settings", "field-table", "locator-detail", "quality-summary", "quality-limitations"]) $(id).replaceChildren();
  $("quality-gate").textContent = "—"; $("rul-value").textContent = "—";
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
    const dt = document.createElement("dt"), dd = document.createElement("dd");
    dt.textContent = key; dd.textContent = fmt(value); target.append(dt, dd);
  });
}

function stats(trend) {
  const values = {Start: trend.start_value, End: trend.end_value, Change: trend.change, "OLS slope": trend.slope, "Pearson r": trend.pearson_correlation, Direction: trend.direction, Samples: trend.sample_count, "Cycle range": `${trend.cycle_start}–${trend.cycle_end}`};
  $("trend-stats").replaceChildren(...Object.entries(values).map(([key, value]) => {
    const box = document.createElement("div"), label = document.createElement("span"), strong = document.createElement("strong");
    box.className = "stat"; label.textContent = key; strong.textContent = fmt(value); box.append(label, strong); return box;
  }));
}

function chart(series, selectedCycle) {
  const svg = $("trend-chart"), points = series.points, width = 900, height = 350, pad = {l: 68, r: 28, t: 24, b: 48};
  svg.replaceChildren(); if (!points.length) return;
  const minX = points[0].cycle, maxX = points.at(-1).cycle;
  let minY = Math.min(...points.map(point => point.value)), maxY = Math.max(...points.map(point => point.value));
  if (minY === maxY) { const margin = Math.max(Math.abs(minY) * 0.01, 1); minY -= margin; maxY += margin; }
  const x = value => pad.l + (value - minX) / Math.max(1, maxX - minX) * (width - pad.l - pad.r);
  const y = value => pad.t + (maxY - value) / (maxY - minY) * (height - pad.t - pad.b);
  const ns = "http://www.w3.org/2000/svg";
  for (let index = 0; index < 5; index += 1) {
    const line = document.createElementNS(ns, "line"); line.setAttribute("x1", pad.l); line.setAttribute("x2", width - pad.r);
    line.setAttribute("y1", pad.t + index * (height - pad.t - pad.b) / 4); line.setAttribute("y2", pad.t + index * (height - pad.t - pad.b) / 4); line.setAttribute("class", "chart-grid"); svg.append(line);
  }
  const path = document.createElementNS(ns, "path");
  path.setAttribute("d", points.map((point, index) => `${index ? "L" : "M"}${x(point.cycle).toFixed(2)},${y(point.value).toFixed(2)}`).join(" "));
  path.setAttribute("class", "chart-line"); svg.append(path);
  const selected = points.find(point => point.cycle === selectedCycle);
  if (selected) { const dot = document.createElementNS(ns, "circle"); dot.setAttribute("cx", x(selected.cycle)); dot.setAttribute("cy", y(selected.value)); dot.setAttribute("r", 7); dot.setAttribute("class", "chart-dot"); svg.append(dot); }
  [[pad.l, height - 16, `Cycle ${minX}`], [width - pad.r - 85, height - 16, `Cycle ${maxX}`], [8, pad.t + 5, fmt(maxY)], [8, height - pad.b, fmt(minY)]].forEach(([xx, yy, text]) => {
    const label = document.createElementNS(ns, "text"); label.setAttribute("x", xx); label.setAttribute("y", yy); label.setAttribute("class", "axis-label"); label.textContent = text; svg.append(label);
  });
}

function renderFields(row, sensor) {
  $("field-table").replaceChildren(...Object.values(row.fields).map(field => {
    const tr = document.createElement("tr"); if (field.canonical_field_name === sensor) tr.className = "selected";
    [field.raw_column_index, field.canonical_field_name, field.raw_value, fmt(field.parsed_value)].forEach(value => { const td = document.createElement("td"); td.textContent = value; tr.append(td); }); return tr;
  }));
}

function renderQuality(data) {
  $("quality-gate").textContent = data.quality_gate;
  const quality = data.quality, structure = data.structure;
  const items = {Structure: structure.passed ? "PASS" : "FAIL", Rows: structure.actual_rows, Units: structure.unit_count, Duplicates: quality.duplicate_full_rows, Missing: quality.missing_values, "Cycle gaps": quality.missing_cycle_units, "Constant fields": Object.values(quality.feature_statistics).filter(item => item.constant).length, "Near constant": Object.values(quality.feature_statistics).filter(item => item.near_constant).length, "Potential outliers": Object.values(quality.feature_statistics).reduce((sum, item) => sum + item.potential_outlier_count, 0), "Source SHA": `${data.source_sha256.slice(0, 12)}…`};
  $("quality-summary").replaceChildren(...Object.entries(items).map(([key, value]) => { const div = document.createElement("div"), label = document.createElement("span"), strong = document.createElement("strong"); div.className = "quality-item"; label.textContent = key; strong.textContent = value; div.append(label, strong); return div; }));
  $("quality-limitations").replaceChildren(...data.limitations.map(text => { const paragraph = document.createElement("p"); paragraph.textContent = `• ${text}`; return paragraph; }));
}

function selectionSnapshot() {
  const snapshot = {split: selectors.split.value, unit: Number(selectors.unit.value), cycle: Number(selectors.cycle.value), sensor: selectors.sensor.value};
  if (!snapshot.split || !snapshot.sensor || !Number.isInteger(snapshot.unit) || !Number.isInteger(snapshot.cycle) || snapshot.unit <= 0 || snapshot.cycle <= 0) {
    const error = new Error("The current selection is incomplete."); error.code = "INVALID_REQUEST"; throw error;
  }
  return snapshot;
}

async function refresh(transaction) {
  const selected = selectionSnapshot(), base = `split=${selected.split}&unit_id=${selected.unit}`;
  const [row, trend, series, ops, quality, locator, rul] = await Promise.all([
    api(`/api/v1/raw-row?${base}&cycle=${selected.cycle}`, transaction), api(`/api/v1/sensor-trend?${base}&sensor_id=${selected.sensor}`, transaction),
    api(`/api/v1/sensor-series?${base}&sensor_id=${selected.sensor}`, transaction), api(`/api/v1/operational-settings?${base}&cycle=${selected.cycle}`, transaction),
    api(`/api/v1/data-quality?split=${selected.split}`, transaction), api(`/api/v1/raw-source-locator?${base}&cycle=${selected.cycle}&field_name=${selected.sensor}`, transaction),
    selected.split === "test" ? api(`/api/v1/test-rul?${base}`, transaction) : Promise.resolve(null),
  ]);
  if (!isCurrent(transaction) || JSON.stringify(selectionSnapshot()) !== JSON.stringify(selected)) return;
  $("selected-value").textContent = fmt(row.fields[selected.sensor].parsed_value); $("selected-sensor").textContent = selected.sensor;
  $("chart-title").textContent = `${selected.sensor} · Unit ${selected.unit}`; $("range-badge").textContent = `Cycle ${series.cycle_start}–${series.cycle_end} · ${series.sample_count} samples`;
  dl($("selection-summary"), {"Dataset Split": selected.split.toUpperCase(), "Engine Unit": selected.unit, Cycle: selected.cycle, "Selected Sensor": selected.sensor});
  $("op-settings").replaceChildren(...[1, 2, 3].map(index => { const div = document.createElement("div"), label = document.createElement("small"), value = document.createElement("strong"); label.textContent = `Setting ${index}`; value.textContent = fmt(ops[`op_setting_${index}`]); div.append(label, value); return div; }));
  renderFields(row, selected.sensor); dl($("locator-detail"), locator); stats(trend); chart(series, selected.cycle); renderQuality(quality);
  $("rul-panel").classList.toggle("hidden", !rul); if (rul) $("rul-value").textContent = `${rul.rul_cycles} cycles`;
  document.querySelector("main").setAttribute("aria-busy", "false"); state("資料已就緒");
}

async function loadCycles(transaction, split, unit) {
  const data = await api(`/api/v1/cycles?split=${split}&unit_id=${unit}`, transaction);
  if (!isCurrent(transaction) || selectors.split.value !== split || Number(selectors.unit.value) !== unit) return;
  if (!data.cycles.length) { const error = new Error("No cycles are available for the selected Unit."); error.code = "EMPTY_QUERY_RESULT"; throw error; }
  setOptions(selectors.cycle, data.cycles); await refresh(transaction);
}

async function loadUnits(transaction, split) {
  const data = await api(`/api/v1/units?split=${split}`, transaction);
  if (!isCurrent(transaction) || selectors.split.value !== split) return;
  if (!data.units.length) { const error = new Error("No Units are available for the selected Split."); error.code = "EMPTY_QUERY_RESULT"; throw error; }
  setOptions(selectors.unit, data.units); await loadCycles(transaction, split, Number(selectors.unit.value));
}

async function init() {
  const transaction = beginTransition("正在驗證本地資料…", "units");
  try {
    const [statusData, splitData, sensorData] = await Promise.all([api("/api/v1/status", transaction), api("/api/v1/splits", transaction), api("/api/v1/sensors", transaction)]);
    if (!isCurrent(transaction)) return;
    if (!statusData.data_available) { const error = new Error("Validated FD001 data is unavailable."); error.code = "SOURCE_INTEGRITY_FAILURE"; throw error; }
    $("validation-status").textContent = statusData.validation_status; $("dataset-id").textContent = statusData.dataset_id;
    $("contract-version").textContent = `Data Contract v${statusData.contract_version} · ${statusData.source_trust_policy}`;
    setOptions(selectors.split, splitData.dataset_splits, item => item.toUpperCase()); setOptions(selectors.sensor, sensorData.sensors.map(item => item.sensor_id));
    await loadUnits(transaction, selectors.split.value);
  } catch (error) { fail(error, transaction); }
}

selectors.split.addEventListener("change", () => { const transaction = beginTransition("更新 Dataset Split…", "units"); loadUnits(transaction, selectors.split.value).catch(error => fail(error, transaction)); });
selectors.unit.addEventListener("change", () => { const split = selectors.split.value, unit = Number(selectors.unit.value), transaction = beginTransition("更新 Engine Unit 與 Cycle…", "cycles"); loadCycles(transaction, split, unit).catch(error => fail(error, transaction)); });
for (const selector of [selectors.cycle, selectors.sensor]) selector.addEventListener("change", () => { const transaction = beginTransition("更新所選資料…"); refresh(transaction).catch(error => fail(error, transaction)); });

init();
