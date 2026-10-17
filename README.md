# CVVH Circuit Motion Design

Motion-design explainer of a CVVH (continuous veno-venous hemofiltration) circuit, modelled on an Infomed HF440 at the bedside. Settings shown are read from a real machine screen: Qb 150 ml/min, replacement 2000 ml/h (50 % pre / 50 % post), net UF 100 ml/h, effluent ≈ 2100 ml/h, anticoagulant 14.2 ml/h.

**Live site:** https://htlin222.github.io/cvvh-circuit-motion-design/ — video, interactive schematic and 3D model (served from `docs/` on `main`).

**Footage:** the 30 s 1920×1080 video (dark mode, with sound) is attached to the [latest release](../../releases/latest).

## Contents

| Path | What it is |
| --- | --- |
| `docs/index.html` | GitHub Pages landing page: embedded video with scene jump links, settings, links to the interactive pages. |
| `docs/schematic.html` | Interactive 2D schematic. Four animated flow lines (blood, replacement, effluent, anticoagulant), 16 tappable components with explanations, layer toggles. Light/dark aware. |
| `docs/3d.html` | Earlier rotating 3D (Three.js) specimen-plate version. |
| `video/video.html` | 1920×1080 video stage. Same schematic, frameless, HUD around the edges, scripted 9-scene timeline. Exposes `render(t)` for deterministic frame capture. |
| `video/sound.py` | Synthesized sci-fi sound design (drone, pump bed, transition whoosh + sub hit + shimmer, HUD blips, zoom servo). numpy/scipy only, no samples. |
| `video/render.py` | Renders frames with Playwright, builds the audio, encodes `dist/CVVH_circuit_30s_1080p.mp4` with ffmpeg. |

## Build the video

```bash
pip install playwright numpy scipy && playwright install chromium
python3 video/render.py
```

Requires ffmpeg and a CJK font (Noto Sans/Serif CJK TC) on the system.

## Timeline

| t (s) | Scene |
| --- | --- |
| 0 | Overview |
| 3 | Arterial draw: A pressure → blood pump |
| 7 | Anticoagulant syringe |
| 10 | Pre-dilution |
| 14 | Hemofilter (convection) |
| 18 | Effluent: P pressure → blood-leak detector → effluent pump |
| 21 | Heater → post-dilution |
| 25 | Return: drip chamber/V → air detector → venous clamp |
| 28 | Summary: net UF = effluent − replacement |

The camera follows one continuous monotone-cubic path through per-scene keyframes, and all highlights/HUD changes crossfade across scene boundaries, so there are no holds or jumps.

## Disclaimer

Educational schematic. Pump roles are inferred from the machine's layout; follow local protocol and the device's own display for actual settings.
