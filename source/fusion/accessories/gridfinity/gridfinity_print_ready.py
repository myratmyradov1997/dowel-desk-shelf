"""Print-ready STLs for the Gridfinity inserts (plain python3 + numpy) and slicer plate plans.
Parts are modelled in print orientation (plates and bins bottom down) - only moved onto the bed centre."""
import json, os, struct
import numpy as np

D = os.path.expanduser('~/fusion-mcp/exports/acc-gridfinity')
RAW, PR = D + '/stl_raw', D + '/print'
os.makedirs(PR, exist_ok=True)
DT = np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')])


def load(fn):
    d = open(fn, 'rb').read()
    n = struct.unpack('<I', d[80:84])[0]
    return d, np.frombuffer(d[84:84+n*50], dtype=DT).copy()


rep = []
for fn in sorted(os.listdir(RAW)):
    if not fn.endswith('.stl'):
        continue
    d, a = load(f'{RAW}/{fn}')
    v = a['v'].reshape(-1, 3).astype(np.float64)
    lo, hi = v.min(0), v.max(0)
    v -= np.array([(lo[0]+hi[0])/2-127.5, (lo[1]+hi[1])/2-105, lo[2]])
    a['v'] = v.reshape(-1, 9).astype(np.float32)
    t = v.reshape(-1, 3, 3)
    nr = np.cross(t[:, 1]-t[:, 0], t[:, 2]-t[:, 0])
    nr /= np.maximum(np.linalg.norm(nr, axis=1, keepdims=True), 1e-12)
    a['n'] = nr.astype(np.float32)
    out = d[:80] + struct.pack('<I', len(a)) + a.tobytes()
    open(f'{PR}/{fn}', 'wb').write(out)
    if fn.startswith('gf_plate'):
        open(f'{PR}/{fn[:-4]}_copy2.stl', 'wb').write(out)
    rep.append(dict(part=fn[:-4], print_dims_mm=[round(float(x), 2) for x in hi-lo], triangles=int(len(a))))
json.dump(rep, open(f'{PR}/print_orientation.json', 'w'), indent=2)
P = lambda n: f'{PR}/{n}.stl'
plates = {
    "gf01_plates_right_drawer_2x_half": [P('gf_plate_R_half_2x5'), P('gf_plate_R_half_2x5_copy2')],
    "gf02_plates_left_drawer_4pcs": [P('gf_plate_Lfront_half_2x3'), P('gf_plate_Lfront_half_2x3_copy2'),
                                     P('gf_plate_Lback_half_2x1'), P('gf_plate_Lback_half_2x1_copy2')],
    "gf03_bin_1x1": [P('gf_bin_1x1_7u')],
    "gf04_bin_1x2": [P('gf_bin_1x2_7u')],
    "gf05_bin_2x2": [P('gf_bin_2x2_7u')],
    "gf06_bin_1x3_dupont": [P('gf_bin_1x3_7u_dupont')],
    "gf07_bins_starter_set_all4": [P('gf_bin_1x1_7u'), P('gf_bin_1x2_7u'), P('gf_bin_2x2_7u'), P('gf_bin_1x3_7u_dupont')],
}
json.dump(plates, open(f'{PR}/plates_fast_028.json', 'w'), indent=2)
print(json.dumps(rep, indent=1))
