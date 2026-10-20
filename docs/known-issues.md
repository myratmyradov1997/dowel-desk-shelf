# Known issues and lessons learned

Things that went wrong or are still open. Read before printing.

## Dowels

- **Diameter varies a lot.** Five "20 mm" dowels from one order: three 20.0–20.1 mm, two 19.0 mm.
  Measure every rod and print `fit_coupon_sockets` first. Inner-leg sockets are a parameter (`SOCK_INNER`).
- **The clamp cannot grip a thin rod.** Pinch clamps (2.4 mm slot) close to ≈ 19.6 mm. Put thin rods in positions 2 and 4.
- **Length differs by up to 1 cm.** Cut to the shortest, or centre each rod; the end-leg sockets are 14 mm deep.
- **Rods are bent.** Assemble bow down. Five tight sockets on five bent rods can jam when you slide an inner leg 30 cm along them —
  that is why the middle socket of the fitted inner leg is looser (D20.4).
- **Wood moves with humidity** (~0.2 mm). Re-tighten the M3 clamps when the heating season starts.

## Fits

- Deck tiles sit loosely on purpose (saddles D21).
- Rod clips: D20.2 slid too easily on 20.0 rods in a PLA test, hence D19.8. Not yet confirmed in ABS.
- Inner-leg sockets D20.2/19.3/20.4 are the author's estimate from a ring test, not printed yet.

## Bugs found and fixed in CAD (before printing)

- **Drawer stop tongue (fixed in v2.4c):** in earlier versions the slots around the stop tongue were cut only 0.5 mm into the
  2 mm side wall, so the tongue was not free and the drawer could not be pushed past the leg. The current STL cuts
  through the whole wall (checked by point probes in the model). If you have an older drawer STL, do not print it.

## Printing

- Legs and tiles are 244 mm long: they need a 245 × 200 mm bed. No Ender-3-size beds without splitting the parts.
- ABS warps on long flat parts: enclosure, 105 °C bed, brim, do not open the door until the part cools.
- A **power cut** killed a 6 h leg print at ~70 %. ABS cools and detaches, so resuming after a long break is pointless — restart.
- The 0.28 mm drawer slide is not yet tested; if it rubs, print the drawer at 0.20 mm, and use paraffin on the channel.

## Not verified yet

- Load capacity and long-term creep of ABS legs under a 6 kg monitor. **No load rating.**
- Whether the whole thing wobbles sideways (a crossed-cable brace is the fallback).
- All accessories (MagSafe v3, Gridfinity, front-rod holders, storage, backlight) — CAD-checked only.
- Storage set is heavy (627 g, 28 h) and its hangers use the same bare rod-5 sections as the backlight brackets
  (x ≈ ±281…326): you cannot install both as they are.
- Backlight rail needs the back 14 mm of the deck — the monitor stand must not sit at the very back edge.
