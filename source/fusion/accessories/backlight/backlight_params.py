"""Shared parameters + 2D sections of the DeskShelf backlight (mm, global shelf coordinates).
Imported by nothing inside Fusion (Fusion script is self-contained); used for quick checks in plain python3."""
import math
LED_W, LED_T, ANG = 10.0, 2.5, 45.0
CH = LED_W + 0.6
LIP_T, LIP_H = 1.2, LED_T + 1.5
G, DIF_T, HOOK_T, NB = 0.05, 0.9, 0.9, 0.9
Z0, ARCH_H, Y_MAX = 118.2, 7.5, 121.8
sA, cA = math.sin(math.radians(ANG)), math.cos(math.radians(ANG))
ARCH_TOP = Z0 + ARCH_H
Z0F = ARCH_TOP + 1.3 + LIP_T * cA
Y0 = Y_MAX - ((LIP_T + G + HOOK_T) * sA + (LIP_H + G + DIF_T) * cA)
def P(s, n):
    return (Y0 - s * sA + n * cA, Z0F + s * cA + n * sA)
def rail_section():
    v3, v10 = P(-LIP_T, 0), P(CH + LIP_T, 0)
    return [(v10[0], Z0), (v3[0], Z0), v3, P(-LIP_T, 1.0), P(-LIP_T + 0.4, 1.5), P(-LIP_T, 2.0), P(-LIP_T, LIP_H),
            P(0, LIP_H), P(0, 0), P(CH, 0), P(CH, LIP_H), P(CH + LIP_T, LIP_H),
            P(CH + LIP_T, 2.0), P(CH + LIP_T - 0.4, 1.5), P(CH + LIP_T, 1.0), v10]
def diffuser_section():
    a, b = -(LIP_T + G), CH + LIP_T + G
    top = LIP_H + G + DIF_T
    return [P(a - HOOK_T, NB), P(a - HOOK_T, top), P(b + HOOK_T, top), P(b + HOOK_T, NB), P(b, NB), P(b, 1.1),
            P(b - 0.35, 1.5), P(b, 1.9), P(b, LIP_H + G), P(a, LIP_H + G), P(a, 1.9), P(a + 0.35, 1.5), P(a, 1.1), P(a, NB)]
if __name__ == "__main__":
    r, d = rail_section(), diffuser_section()
    print("Y0 %.2f Z0F %.2f" % (Y0, Z0F))
    for nm, pts in (("rail", r), ("diff", d)):
        ys, zs = [p[0] for p in pts], [p[1] for p in pts]
        print(nm, "y %.2f..%.2f z %.2f..%.2f" % (min(ys), max(ys), min(zs), max(zs)))
        print(" ", [(round(a, 2), round(b, 2)) for a, b in pts])
