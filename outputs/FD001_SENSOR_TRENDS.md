# FD001 Traceable Sensor Trend Analysis

- Train and Test are analyzed independently.
- Start/end are the first/last valid cycles in original raw order.
- Change is end minus start.
- Slope is OLS `sum((x-x_mean)(y-y_mean))/sum((x-x_mean)^2)`.
- Pearson correlation uses centered covariance divided by the product of centered square-root sums.
- Undefined denominators remain `UNDEFINED`; they are never replaced with zero.
- Direction tolerance is `1e-12 × max(1, abs(mean_sensor)) / max(1, cycle_range)`.
- Direction ratios exclude undefined results from the denominator.

## Cycle-length distributions

| Split | Units | Min cycles | Max cycles | Mean | Population SD | Median | Unique lengths |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train | 100 | 128 | 362 | 206.31 | 46.1104532617 | 199 | 66 |
| test | 100 | 31 | 303 | 130.96 | 53.3248384901 | 133.5 | 80 |

## Train sensor trends

- Per-unit/per-sensor analyses completed: `2100` of `2100`.

| Sensor | Min | Max | Mean | Population SD | Global cycle correlation | Increasing | Decreasing | Flat | Undefined | Increasing ratio | Decreasing ratio | Flat ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sensor_01 | 518.67 | 518.67 | 518.67 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_02 | 641.21 | 644.53 | 642.680933547 | 0.500041150936 | 0.549898040647 | 100 | 0 | 0 | 0 | 1 | 0 | 0 |
| sensor_03 | 1571.04 | 1616.91 | 1590.52311861 | 6.13100092719 | 0.543946996738 | 100 | 0 | 0 | 0 | 1 | 0 | 0 |
| sensor_04 | 1382.25 | 1441.49 | 1408.93378169 | 9.00038664488 | 0.624577166332 | 100 | 0 | 0 | 0 | 1 | 0 | 0 |
| sensor_05 | 14.62 | 14.62 | 14.62 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_06 | 21.6 | 21.61 | 21.6098032088 | 0.00138895124973 | 0.10597998499 | 61 | 1 | 38 | 0 | 0.61 | 0.01 | 0.38 |
| sensor_07 | 549.85 | 556.06 | 553.367711211 | 0.885070806862 | -0.595913555809 | 0 | 100 | 0 | 0 | 0 | 1 | 0 |
| sensor_08 | 2387.9 | 2388.56 | 2388.09665164 | 0.0709837585105 | 0.475977318859 | 100 | 0 | 0 | 0 | 1 | 0 | 0 |
| sensor_09 | 9021.73 | 9244.59 | 9065.24294072 | 22.0823443317 | 0.443999347239 | 71 | 29 | 0 | 0 | 0.71 | 0.29 | 0 |
| sensor_10 | 1.3 | 1.3 | 1.3 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_11 | 46.85 | 48.53 | 47.541168145 | 0.267080925598 | 0.634384504836 | 100 | 0 | 0 | 0 | 1 | 0 | 0 |
| sensor_12 | 518.69 | 523.38 | 521.413470021 | 0.737535517111 | -0.611353633028 | 0 | 100 | 0 | 0 | 0 | 1 | 0 |
| sensor_13 | 2387.88 | 2388.56 | 2388.09615239 | 0.0719171726956 | 0.477522963497 | 100 | 0 | 0 | 0 | 1 | 0 | 0 |
| sensor_14 | 8099.94 | 8293.72 | 8143.75272212 | 19.0757136521 | 0.370323634198 | 60 | 40 | 0 | 0 | 0.6 | 0.4 | 0 |
| sensor_15 | 8.3249 | 8.5848 | 8.44214558189 | 0.0375041289923 | 0.58867578391 | 100 | 0 | 0 | 0 | 1 | 0 | 0 |
| sensor_16 | 0.03 | 0.03 | 0.03 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_17 | 388 | 400 | 393.21065387 | 1.54872548931 | 0.566994911452 | 100 | 0 | 0 | 0 | 1 | 0 | 0 |
| sensor_18 | 2388 | 2388 | 2388 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_19 | 100 | 100 | 100 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_20 | 38.14 | 39.43 | 38.8162706607 | 0.180742047363 | -0.583596891906 | 0 | 100 | 0 | 0 | 0 | 1 | 0 |
| sensor_21 | 22.8942 | 23.6184 | 23.2897053609 | 0.108248251213 | -0.585923382121 | 0 | 100 | 0 | 0 | 0 | 1 | 0 |

## Test sensor trends

- Per-unit/per-sensor analyses completed: `2100` of `2100`.

| Sensor | Min | Max | Mean | Population SD | Global cycle correlation | Increasing | Decreasing | Flat | Undefined | Increasing ratio | Decreasing ratio | Flat ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sensor_01 | 518.67 | 518.67 | 518.67 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_02 | 641.13 | 644.3 | 642.475087813 | 0.400884035607 | 0.348094184772 | 90 | 10 | 0 | 0 | 0.9 | 0.1 | 0 |
| sensor_03 | 1569.04 | 1607.55 | 1588.09920434 | 5.00308290349 | 0.32212116703 | 93 | 7 | 0 | 0 | 0.93 | 0.07 | 0 |
| sensor_04 | 1384.39 | 1433.36 | 1404.73536194 | 6.68805393109 | 0.428696563106 | 94 | 6 | 0 | 0 | 0.94 | 0.06 | 0 |
| sensor_05 | 14.62 | 14.62 | 14.62 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_06 | 21.6 | 21.61 | 21.609700672 | 0.00170401969354 | 0.0768246906591 | 53 | 13 | 34 | 0 | 0.53 | 0.13 | 0.34 |
| sensor_07 | 550.88 | 555.84 | 553.757522908 | 0.681260097868 | -0.404598311179 | 6 | 94 | 0 | 0 | 0.06 | 0.94 | 0 |
| sensor_08 | 2387.89 | 2388.3 | 2388.07096442 | 0.0574395909986 | 0.312228761848 | 93 | 7 | 0 | 0 | 0.93 | 0.07 | 0 |
| sensor_09 | 9024.53 | 9155.03 | 9058.40736332 | 11.4358238812 | 0.340686819884 | 75 | 25 | 0 | 0 | 0.75 | 0.25 | 0 |
| sensor_10 | 1.3 | 1.3 | 1.3 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_11 | 46.8 | 48.26 | 47.4162041845 | 0.195909765129 | 0.446071309944 | 96 | 4 | 0 | 0 | 0.96 | 0.04 | 0 |
| sensor_12 | 519.38 | 523.76 | 521.747723732 | 0.559605386948 | -0.416961513436 | 4 | 96 | 0 | 0 | 0.04 | 0.96 | 0 |
| sensor_13 | 2387.89 | 2388.32 | 2388.07102474 | 0.0569321365511 | 0.310481111208 | 90 | 10 | 0 | 0 | 0.9 | 0.1 | 0 |
| sensor_14 | 8108.5 | 8220.48 | 8138.94781689 | 10.1882159757 | 0.257983585735 | 63 | 37 | 0 | 0 | 0.63 | 0.37 | 0 |
| sensor_15 | 8.3328 | 8.5414 | 8.42584396762 | 0.02900821996 | 0.385035736836 | 96 | 4 | 0 | 0 | 0.96 | 0.04 | 0 |
| sensor_16 | 0.03 | 0.03 | 0.03 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_17 | 389 | 397 | 392.571624924 | 1.23352972728 | 0.361175668083 | 92 | 8 | 0 | 0 | 0.92 | 0.08 | 0 |
| sensor_18 | 2388 | 2388 | 2388 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_19 | 100 | 100 | 100 | 0 | UNDEFINED | 0 | 0 | 100 | 0 | 0 | 0 | 1 |
| sensor_20 | 38.31 | 39.41 | 38.8925015272 | 0.141675345888 | -0.384333329888 | 6 | 94 | 0 | 0 | 0.06 | 0.94 | 0 |
| sensor_21 | 22.9354 | 23.6419 | 23.3357426924 | 0.0841170684159 | -0.376825490425 | 8 | 92 | 0 | 0 | 0.08 | 0.92 | 0 |

## Test last-observation and RUL relationship

- Alignment result: `PASS`
- Test last observed cycle range: `31..303`
- RUL cycle range: `7..145`
- Convention-derived last-observed-plus-RUL range: `141..341`
- The last observed Test cycle is not labeled as a failure cycle. The mapping is a validated format convention, not an independently proven physical-engine relationship.

## Traceability and limitations

Each local per-unit/per-sensor result contains split, unit, sensor, cycle range, N, OLS/Pearson results, source SHA-256, and first/last raw-line plus raw-column locators. Full details and series are rebuilt in memory and are not committed.

Correlation is not causation. Trend direction is not a validated fault diagnosis and this work does not implement an RUL prediction model.
