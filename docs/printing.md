# Printing

All STL files are already in print orientation, centred on a 255 × 210 bed. **No supports** except the MagSafe cup
(supports only inside the puck pocket and cable notch).

## Settings used (ABS, FlyingBear Ghost 6, OrcaSlicer)

| Profile (`source/orca/…`) | Used for | Settings |
|---|---|---|
| `abs_quality` | test prints, small parts, MagSafe, accessories | 0.20 mm, 4 walls, 20 % gyroid, 250 / 105 °C, flow 0.987 |
| `abs_fast_020` | legs | as above, but infill every second layer (0.40) — sockets and channel stay at 0.20 |
| `abs_fast_028` | drawers, modules, bins | 0.28 mm, line width 0.45–0.50 |
| `abs_fast_028_tile` | deck tiles | 0.28 mm with 3 top / 3 bottom solid layers (−28 g per tile, same look) |

The profiles are flattened copies for the Orca CLI (`source/orca/slice_plates.py`). Machine limits of the Ghost 6
used: acceleration 1500 mm/s², ABS max volumetric flow 15 mm³/s. Adapt to your printer.

ABS tips that mattered: enclosure closed until the part is below ~45 °C, 105 °C bed, glue stick, brim 5 mm on the long
parts, dry filament (60 °C, 4 h).

## Parts list

| # | Part | Qty | Colour in the photos | Weight / time (Ghost 6) |
|---|---|---|---|---|
| 0 | `fit_coupon_sockets`, `fit_coupon_slide_leg` + `fit_coupon_slide_drawer` | 1 each | any | ≈ 20 g / 1.5 h |
| 1 | `leg_end_left_D20.4`, `leg_end_right_D20.4` | 1 each | grey | 106–110 g / 6.3–8.6 h each |
| 2 | `leg_inner_left_*`, `leg_inner_right_*` (pick the variant) | 1 each | grey | 93 g / 5.6 h each |
| 3 | `deck_tile_1`, `deck_tile_2`, `deck_tile_3` (dovetails) **or** 3 × `deck_tile_wrap_v2.5` (experimental) | 1 each / 3 | grey / blue | 94–105 g / 4.4–5.9 h each; wrap tile 105 g / 4.6 h |
| 4 | `rod_clip_D19.8` (or `_D20.2`) | 2 | grey | small |
| 5 | `bay_gauge` (194 mm spacer for assembly) | 1 | any | small |
| 6 | `drawer_right` (v2.5c) | 1 | blue | 199 g / 6.4 h (0.28) |
| 7 | `drawer_left` (v2.5c, with a divider, printed in one piece) | 1 | blue | 220 g / 7.1 h (0.28) |
| 8 | `laptop_dock` + `bookend` | 1 each | blue | 116 g / 5.2 h |
| 9 | `macmini_stand` | 1 | blue | 64 g / 2.7 h |

Total for shelf + modules ≈ 1.34 kg.

**Suggested print order:** test prints → one end leg → try a dowel in it → the remaining legs →
tiles → clips and gauge → change colour → right drawer → check the slide → left drawer → modules.

## Checks on the first parts

1. **Socket ring:** push each dowel into D20.2 / 20.4 / 20.6 (1/2/3 notches). Pick the size per dowel position.
2. **Slide coupons:** the drawer flange must slide in the leg channel without rubbing and with little side play.
   The channel geometry (45° V, 0.5 mm above the rim, 2.8 mm deep) was chosen from three variants this way.
3. **First drawer:** test it in a printed leg before printing the second one. If it is tight at 0.28 mm,
   print the second drawer at 0.20.
