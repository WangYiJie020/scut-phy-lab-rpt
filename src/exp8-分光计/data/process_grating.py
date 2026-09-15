#!/usr/bin/env python3
"""Spectrometer grating reduction for exp8.

Angles are (deg, arcmin). After the raw-record readings are confirmed,
update EXTRACTED and run this file.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def dms(deg: float, minutes: float = 0.0) -> float:
    return deg + minutes / 60.0


def wrap_diff(a: float, b: float) -> float:
    x = abs(a - b)
    if x > 180.0:
        x = 360.0 - x
    return x


def phi_from_windows(right_left: float, right_right: float,
                     left_left: float, left_right: float) -> float:
    return 0.25 * (
        wrap_diff(right_left, left_left) + wrap_diff(right_right, left_right)
    )


def fmt_ang(deg: float) -> str:
    sign = "-" if deg < 0 else ""
    deg = abs(deg)
    d = int(math.floor(deg + 1e-12))
    m = (deg - d) * 60.0
    if abs(m - 60.0) < 1e-6:
        d += 1
        m = 0.0
    return f"{sign}{d}°{m:05.2f}'".replace(".00'", "'")


@dataclass
class Line:
    name: str
    k: int
    right_left: tuple[float, float]
    right_right: tuple[float, float]
    left_left: tuple[float, float]
    left_right: tuple[float, float]
    phi_written: float | None = None


# Provisional readings pending user confirmation.
EXTRACTED = [
    Line("green", 1, (336, 30), (156, 30), (342, 45), (162, 45), None),
    Line("green", 2, (328, 50), (148, 50), (341, 30), (161, 30), None),
    Line("unknown", 1, (328, 55), (148, 55), (347, 45), (167, 45), None),
    Line("unknown", 2, (357, 30), (177, 30), (319, 10), (139, 10), None),
    Line("yellow_I", 1, (328, 30), (148, 30), (348, 20), (168, 20), None),
    Line("yellow_II", 1, (358, 30), (178, 30), (338, 30), (158, 30), None),
]
# Use recalculated phi, not handwritten estimates.


D_KNOWN_MM = 0.01
LAMBDA_GREEN_NM = 546.07
LAMBDA_YI_NM = 576.96
LAMBDA_YII_NM = 579.07


def reduce_line(line: Line) -> dict:
    rl, rr, ll, lr = (dms(*x) for x in (
        line.right_left, line.right_right, line.left_left, line.left_right
    ))
    phi = phi_from_windows(rl, rr, ll, lr)
    k = abs(line.k)
    out = {
        "name": line.name,
        "k": line.k,
        "phi_recalc_deg": phi,
        "phi_written_deg": line.phi_written,
        "phi_used_deg": phi,
    }
    phi_used = math.radians(out["phi_used_deg"])
    if line.name == "green":
        lam = D_KNOWN_MM * 1e6 * math.sin(phi_used) / k
        out["lambda_nm"] = lam
        out["lambda_ref_nm"] = LAMBDA_GREEN_NM
        out["rel_err_pct"] = (lam - LAMBDA_GREEN_NM) / LAMBDA_GREEN_NM * 100.0
    elif line.name.startswith("yellow"):
        # filled after unknown-d average in main()
        out["lambda_nm"] = None
    else:
        d_mm = k * LAMBDA_GREEN_NM * 1e-6 / math.sin(phi_used)
        out["d_mm"] = d_mm
        out["N_per_mm"] = 1.0 / d_mm
    return out


def main() -> None:
    print(f"{'name':<10} {'k':>2} {'φ_recalc':>10} {'φ_written':>10} {'result':>14} {'ref':>10} {'err%':>8}")
    for line in EXTRACTED:
        r = reduce_line(line)
        written = "" if r["phi_written_deg"] is None else f"{r['phi_written_deg']:.3f}"
        if "lambda_nm" in r:
            result = f"{r['lambda_nm']:.2f} nm"
            ref = f"{r['lambda_ref_nm']:.2f}"
            err = f"{r['rel_err_pct']:+.2f}"
        else:
            result = f"N={r['N_per_mm']:.1f}/mm"
            ref = ""
            err = ""
        print(f"{r['name']:<10} {r['k']:>2} {r['phi_recalc_deg']:10.3f} {written:>10} {result:>14} {ref:>10} {err:>8}")


if __name__ == "__main__":
    main()
