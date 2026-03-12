Hosted at https://power.internetuniverse.org
# IETF Governance Power Map

A force-directed graph visualization of the ~382 people who hold active governance
positions in IETF/IAB/IRTF/IESG, plus 119 "shadow" authors discovered via coauthorship
analysis. Built from live IETF Datatracker API data (March 2026).

## Serving

The output is a single self-contained HTML file with all data embedded inline.
No build step, no server, no dependencies beyond a browser.

```bash
# Simplest possible deploy
cp output/index.html /var/www/html/ietf-power-map.html

# Or just open locally
open output/index.html
```

The file loads D3.js v7.8.5 from cdnjs and Helvetica Neue from Google Fonts.
Everything else (data, CSS, JS) is inline.

## File Structure

```
archive/
├── README.md
├── output/
│   ├── index.html                          # Current version (v4, 382 people)
│   └── versions/
│       ├── v1_governance_only.html         # 263 governance nodes, org-colored
│       ├── v2_temporal.html                # + RFC timeline, era scrubber
│       ├── v3_enriched_263.html            # + corporate, gender, career timelines
│       └── v4_full_382.html                # + 119 shadow authors, coauthorship edges
├── data/                                   # Raw data fetched from IETF Datatracker API
│   ├── ietf_data.json                      # Governance roles, person names, group metadata
│   ├── rfc_counts.json                     # RFC authorship count per governance person
│   ├── profiles.json                       # Top 100 author RFC timelines + affiliations
│   ├── profiles_full.json                  # All 263 governance author timelines
│   ├── shadow_authors.json                 # 119 non-governance prolific coauthors (metadata)
│   ├── shadow_profiles.json                # Shadow author RFC timelines + affiliations
│   ├── temporal_data.json                  # Decade histograms for top authors
│   ├── enriched.json                       # Normalized companies, gender, sectors
│   └── ietf.db                             # SQLite (intermediate, from earlier build)
└── build/                                  # Computed graph datasets + build scripts
    ├── graph_data.json                     # Raw graph (263 nodes + governance edges)
    ├── graph_trimmed.json                  # Trimmed graph for v1
    ├── graph_temporal.json                 # + temporal/coauthorship for v2
    ├── graph_final.json                    # + corporate/gender for v3 (263 nodes)
    ├── graph_v4.json                       # Final graph (382 nodes, 689 edges)
    ├── build_app.py                        # v2 HTML builder
    ├── build_v3.py                         # v3 HTML builder (generates ietf_v3.html)
    └── build_v4.py                         # v4 HTML builder (generates ietf_v3.html, patched to v4)
```

## Data Sources

All data fetched from the IETF Datatracker REST API:
- `https://datatracker.ietf.org/api/v1/group/role/` — governance roles (IAB, IESG, WG/RG chairs, ADs)
- `https://datatracker.ietf.org/api/v1/person/person/{id}/` — person names, bios, photos
- `https://datatracker.ietf.org/api/v1/doc/documentauthor/?person={id}&document__type=rfc` — RFC authorship + affiliations
- `https://datatracker.ietf.org/api/v1/doc/documentauthor/?document__name=rfc{N}` — coauthor discovery

### Temporal trick
RFC numbers are monotonically increasing and roughly linear with time.
Rather than fetching individual RFC metadata (tar pit), we use a 30-point
`rfc_number → year` interpolation table built from known publication dates.
Accuracy: ±1 year. Resolution: 5-year buckets.

### Gender inference
First-name-based. ~51% unresolved (non-Western names, initials, ambiguous).
Of resolved: ~10% female. Flagged as a limitation in the UI.

### Company normalization
Raw affiliation strings from RFC metadata are regex-normalized to canonical
company names (e.g., "Cisco Systems, Inc." → "Cisco"). 35 companies tracked.

## Graph Layers (segmented control in Graph tab)

| Layer | Node Size | Node Color | Signal |
|-------|-----------|------------|--------|
| Governance | weight score | org body (IAB/IESG/IRTF/WG) | Institutional power |
| RFC | √(RFC count) | cold→hot gradient | Output volume |
| Temporal | years active | gold→cyan (old→new) | Longevity |
| Corporate | √(RFC count) | employer brand color | Company allegiance |
| Gender | governance weight | blue/pink/gray | Demographics |

## Scoring

Governance weight: `IAB=5, IESG=5, Area Director=4, IRTF RG Chair=3, WG Chair=1`
Combined power: `weight×3 + rfcCount + span×0.5`
Corporate index: `people×3 + rfcs + gov_weight×2`

## Rebuilding

The build scripts in `build/` are standalone Python 3 — no dependencies beyond stdlib.
They read from `data/` JSON files and produce self-contained HTML.

```bash
# Rebuild v4 from existing data (no network required)
python3 build/build_v4.py
# Output: ietf_v3.html (then patched inline — see conversation for patch commands)
```

To refresh from live API data, re-run the data collection steps from the conversation.
Rate limit: ~100ms between requests to be polite to datatracker.ietf.org.

## Design

Pre-iOS 7 skeuomorphic (iPhone HIG 2008-2012):
- Linen texture background
- Steel gradient navigation bar with text shadows
- Glossy black tab bar
- Grouped rounded-rect table views with disclosure chevrons
- Embossed gradient badges
- 44pt minimum touch targets
- `-webkit-overflow-scrolling: touch` for momentum scroll
