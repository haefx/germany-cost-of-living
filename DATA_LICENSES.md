# Data Licenses and Provenance

This file lists every external or reference dataset bundled with or called by
the application, separate from the MIT license covering the source code
itself (see [`LICENSE`](LICENSE)). See [`docs/data-provenance.md`](docs/data-provenance.md)
for the full per-city breakdown and freshness details.

## City reference dataset (`data/reference/cities_reference_2023.csv`)

- **Status**: hand-compiled reference/demo figures, modeled on publicly
  known German cost-of-living patterns for the ten cities listed. The figures
  are attributed, by name, to the kinds of sources that publish this type of
  data in Germany — Destatis (Federal Statistical Office), the
  Bundesagentur für Arbeit (Federal Employment Agency), and the BBSR
  Wohnatlas — because they are modeled on that style of publication.
- **What this is not**: this dataset was not re-fetched from a live,
  license-verified API or download in this session. It should be treated as
  a realistic placeholder for demonstration purposes, not as a redistribution
  of a specific licensed government dataset. Before using these figures for
  anything beyond a demo, replace them with a real, license-checked extract
  from the primary source (see the pipeline adapter interface in
  `apps/api/app/pipeline/adapters/`, designed to make that swap
  straightforward).
- **License of the figures as bundled here**: released under the same MIT
  license as the rest of the repository, since they are the project's own
  compiled reference numbers rather than a redistributed dataset.

## Postal-code lookup (zippopotam.us)

- **Source**: [api.zippopotam.us](https://api.zippopotam.us) — a free, public,
  no-authentication API providing place names for a given country/postal code.
- **License**: the service is free to use for this kind of lookup; no
  attribution requirement is imposed by the provider beyond normal fair use.
  No data from this API is stored permanently by the application — it is used
  transiently to resolve a postal code to a city/state name.
- **Fallback**: a static, offline postal-code dataset is not bundled in this
  phase. See [`docs/phase-2-roadmap.md`](docs/phase-2-roadmap.md).

## Fonts, icons, and UI assets

- Icons: [Lucide](https://lucide.dev) (ISC license).
- No third-party fonts are loaded from external CDNs; the system font stack
  is used, in line with the project's privacy requirements.
