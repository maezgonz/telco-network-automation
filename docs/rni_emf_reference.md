# Non-Ionizing Radiation (RNI/EMF) Analysis — Reference

> Reference for electromagnetic-field immission/emission analysis around radio infrastructure, following ICNIRP guidelines (public international standard) and regulatory measurement practice. Distilled from measurement-engineering work producing regulator-facing certified reports.

## 1. Concepts: emission vs immission

| Concept | What it measures | Where |
|---|---|---|
| **Emission** | Power the transmitter radiates | At the antenna / equipment |
| **Immission** | Field strength a PERSON is exposed to | At accessible locations (ground level, rooftops, occupied areas) |

Regulatory compliance is about **immission**: what people are actually exposed to, not what antennas radiate.

## 2. ICNIRP reference levels (public standard)

ICNIRP guidelines define reference levels per frequency band for general public exposure. For the mobile bands (roughly 700 MHz – 3.6 GHz including 5G NR), the electric-field reference levels are in the range of ~40–61 V/m (general public, uncontrolled environment) — always consult the current ICNIRP publication and your local regulator's transposition, which may be stricter.

Key principle: **compliance is assessed per frequency with additive accounting** — when multiple transmitters contribute at one point, the power-sum across frequencies must be checked (Σ(E_i/E_ref,i)² ≤ 1), not each transmitter in isolation.

## 3. Measurement methodology

| Aspect | Practice |
|---|---|
| Equipment | Calibrated broadband field-strength meters (isotropic, 3-axis probes) |
| Points | Worst-case accessible locations: directly under antennas, adjacent rooftops, balconies facing antennas, ground level |
| Sampling | Spatial scanning per point (max-hold) + time averaging per regulation |
| Documentation | Point coordinates, equipment calibration certificate, measurement conditions |

## 4. From raw probes to certified reports

The analysis workflow (distilled from measurement-engineering experience):

1. **Site model**: antenna positions, heights, azimuths, tilts, power
2. **Measurement campaign**: worst-case points + spatial scans
3. **Statistical processing**: max-hold distributions, averages against the integration window the regulation mandates
4. **Histograms**: the regulation-facing deliverable — exposure distribution per point
5. **Verdict**: compliant / non-compliant per point, with margins
6. **Certified report**: equipment traceability, methodology, results, conclusions for regulatory approval

## 5. Hot-spot identification & mitigation

- **Spatial analysis** of measurement grids identifies electromagnetic "hot spots" (localized exposure maxima)
- Mitigation levers, in order of operational preference:
  1. **Antenna re-tilt / re-azimuth** (change the pattern footprint — lowest cost)
  2. **Power reduction** where coverage permits (requires RF engineering validation)
  3. **Site reconfiguration** (relocation, height change — last resort, new permits)

## 6. Why an RF engineer should care

RNI compliance is a hard regulatory gate for site deployment and co-location — a site that fails immission assessment does not go on air. The data-driven spatial analysis behind it is also a genuinely quantitative discipline: statistical distributions, calibration-uncertainty budgets and hypothesis testing against regulatory thresholds.
