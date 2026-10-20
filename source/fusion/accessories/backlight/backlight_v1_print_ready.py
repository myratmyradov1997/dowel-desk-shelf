"""Print-oriented copies of the backlight STLs (plain python3 + numpy).
Rails: as modelled (bottom on the bed). Brackets and box: ring axis vertical (x -> z, ring side on the bed).
Lid: outer face down. Diffusers: outer face down, hooks up."""
import json, os, struct, math
import numpy as np
D = os.path.expanduser('~/fusion-mcp/exports/acc-backlight')
ANG = 45.0
XUP = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float)          # (x,y,z) -> (y,z,x)
LID = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)         # y -> z
f = math.radians(-90 - ANG)
DIF = np.array([[1, 0, 0], [0, math.cos(f), -math.sin(f)], [0, math.sin(f), math.cos(f)]])
ROT = {'rail': np.eye(3), 'bracket': XUP, 'box_lid': LID, 'box': XUP, 'diffuser': DIF}
def load(fn):
    d = open(fn, 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
    return d, np.frombuffer(d[84:84 + n * 50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')])).copy()
rep = []
for fn in sorted(os.listdir(D)):
    if not (fn.startswith('acc_backlight_') and fn.endswith('.stl')):
        continue
    name = fn[:-4]
    key = next(k for k in ('box_lid', 'rail', 'bracket', 'box', 'diffuser') if name.startswith('acc_backlight_' + k))
    d, a = load(os.path.join(D, fn)); v = a['v'].reshape(-1, 3).astype(np.float64) @ ROT[key].T
    lo, hi = v.min(0), v.max(0)
    v -= np.array([(lo[0] + hi[0]) / 2 - 127.5, (lo[1] + hi[1]) / 2 - 105, lo[2]])
    a['v'] = v.reshape(-1, 9).astype(np.float32)
    t = v.reshape(-1, 3, 3); nr = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    nr /= np.maximum(np.linalg.norm(nr, axis=1, keepdims=True), 1e-12); a['n'] = nr.astype(np.float32)
    open(os.path.join(D, 'print', fn), 'wb').write(d[:84] + a.tobytes())
    rep.append(dict(part=name, print_dims_mm=[round(float(x), 1) for x in hi - lo]))
json.dump(rep, open(os.path.join(D, 'print', 'print_orientation.json'), 'w'), indent=2); print(json.dumps(rep, indent=1))
P = os.path.join(D, 'print')
plates = {"backlight_ash": [os.path.join(P, 'acc_backlight_%s.stl' % n) for n in
                            ('rail_S1', 'rail_S2', 'rail_S3', 'bracket_L', 'bracket_R', 'box', 'box_lid')],
          "backlight_diffusers_white": [os.path.join(P, 'acc_backlight_diffuser_%s.stl' % n) for n in ('S1', 'S2', 'S3')]}
json.dump(plates, open(os.path.join(P, 'plates.json'), 'w'), indent=2)
