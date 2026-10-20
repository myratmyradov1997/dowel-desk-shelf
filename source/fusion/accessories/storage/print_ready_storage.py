"""Print-oriented copies of the acc-storage STLs (plain python3 + numpy).
- tray segments, tool rail, headphone foot: as modelled (z up, floor / teeth on the bed)
- tray hangers and the headphone post: on their outer side face (x becomes z) -> all profiles in the bed plane
- pins: head down
Writes exports/acc-storage/print/*.stl, print_orientation.json and plates json for slice_plates.py."""
import json, os, struct
import numpy as np

D = os.path.expanduser('~/fusion-mcp/exports/acc-storage')
BED = (255.0, 210.0, 210.0)
os.makedirs(D + '/print', exist_ok=True)
RX90 = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])      # z' = y  (min y on the bed)
RX180 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])    # z' = -z (head on top -> down)
RY_P = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])      # z' = -x (max x on the bed)
RY_M = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])      # z' = x  (min x on the bed)
ROT = {'tray_hanger_R': RY_P, 'tray_hanger_L': RY_M, 'hp_post': RY_M,
       'tray_pin_1': RX90, 'hp_pin': RX90, 'tray_lock_pin_R': RX180}
NAMES = ['tray_end_L', 'tray_end_R', 'tray_mid', 'tray_hanger_L', 'tray_hanger_R', 'tray_pin_1',
         'tray_lock_pin_R', 'tool_rail', 'hp_foot', 'hp_post', 'hp_pin']


def load(fn):
    d = open(fn, 'rb').read()
    n = struct.unpack('<I', d[80:84])[0]
    return d, np.frombuffer(d[84:84+n*50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')])).copy()


rep = []
for name in NAMES:
    d, a = load(f'{D}/stl/{name}.stl')
    v = a['v'].reshape(-1, 3).astype(np.float64)
    if name in ROT:
        v = v @ ROT[name].T
    lo, hi = v.min(0), v.max(0)
    dims = hi - lo
    if dims[1] > dims[0]:
        v = v[:, [1, 0, 2]] * np.array([1, -1, 1])
        lo, hi = v.min(0), v.max(0)
        dims = hi - lo
    v -= np.array([(lo[0]+hi[0])/2-BED[0]/2, (lo[1]+hi[1])/2-BED[1]/2, lo[2]])
    a['v'] = v.reshape(-1, 9).astype(np.float32)
    t = v.reshape(-1, 3, 3)
    nr = np.cross(t[:, 1]-t[:, 0], t[:, 2]-t[:, 0])
    nr /= np.maximum(np.linalg.norm(nr, axis=1, keepdims=True), 1e-12)
    a['n'] = nr.astype(np.float32)
    out = 'tray_pin' if name == 'tray_pin_1' else 'tray_lock_pin' if name == 'tray_lock_pin_R' else name
    open(f'{D}/print/{out}.stl', 'wb').write(d[:84] + a.tobytes())
    q = np.round(v, 4)
    u, inv = np.unique(q, axis=0, return_inverse=True)
    tri = inv.reshape(-1, 3)
    e = np.sort(np.concatenate([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]]), axis=1)
    _, cnt = np.unique(e, axis=0, return_counts=True)
    rep.append(dict(part=out, print_dims_mm=[round(float(x), 1) for x in dims], watertight=bool((cnt == 2).all()),
                    fits_bed_with_5mm_brim=bool(dims[0]+10 <= BED[0] and dims[1]+10 <= BED[1] and dims[2] <= BED[2])))
json.dump(rep, open(f'{D}/print/print_orientation.json', 'w'), indent=2)
P = D + '/print/'
plates_fast = {
    "01_tray_mid": [P+'tray_mid.stl'],
    "02_tray_end_R": [P+'tray_end_R.stl'],
    "03_tray_end_L": [P+'tray_end_L.stl'],
    "04_tray_hangers": [P+'tray_hanger_L.stl', P+'tray_hanger_R.stl'],
    "05_tool_rail_hp_foot": [P+'tool_rail.stl', P+'hp_foot.stl'],
    "06_hp_post": [P+'hp_post.stl'],
}
plates_quality = {"07_pins": [P+'tray_pin.stl']*8 + [P+'tray_lock_pin.stl']*2 + [P+'hp_pin.stl']}
json.dump(plates_fast, open(P+'plates_fast_028.json', 'w'), indent=1)
json.dump(plates_quality, open(P+'plates_quality_pins.json', 'w'), indent=1)
for r in rep:
    print(r)
