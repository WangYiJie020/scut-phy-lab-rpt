"""Recompute the Richardson-fit results for exp1-电子逸出功.

Input data are the user-corrected raw currents transcribed from
signed_RawRecord.jpg. Currents in the table are recorded in microampere.
"""

from __future__ import annotations

import math


UA_VALUES = [16, 25, 36, 49, 64, 81, 100]
RAW_DATA_UA = {
    0.600: [62, 63, 64, 68, 70, 73, 73],
    0.625: [117, 121, 125, 130, 134, 136, 140],
    0.650: [213, 224, 230, 237, 244, 252, 260],
    0.675: [374, 393, 408, 418, 432, 441, 452],
    0.700: [629, 669, 698, 720, 741, 756, 776],
}


def linfit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 if ss_tot == 0 else 1 - ss_res / ss_tot
    return slope, intercept, r2


def main() -> None:
    sqrt_u = [math.sqrt(u) for u in UA_VALUES]
    temperatures: list[float] = []
    lg_i0_values: list[float] = []

    print("Per-temperature fit: lg(Ia/uA) = a * sqrt(Ua) + b")
    for filament_current, row in RAW_DATA_UA.items():
        lg_ia = [math.log10(value) for value in row]
        slope, intercept, r2 = linfit(sqrt_u, lg_ia)
        temperature = 900 + 1430 * filament_current
        temperatures.append(temperature)
        lg_i0_values.append(intercept)
        print(
            f"If={filament_current:.3f} A, T={temperature:.2f} K, "
            f"a={slope:.8f}, b={intercept:.8f}, R^2={r2:.6f}, "
            f"I0={10 ** intercept:.8f} uA"
        )
        print("  points:", " ".join(f"({x:.4f},{y:.4f})" for x, y in zip(sqrt_u, lg_ia)))

    inv_t = [1.0 / temperature for temperature in temperatures]
    lg_i_over_t2 = [
        lg_i0 - 2 * math.log10(temperature)
        for lg_i0, temperature in zip(lg_i0_values, temperatures)
    ]
    richardson_slope, richardson_intercept, richardson_r2 = linfit(inv_t, lg_i_over_t2)
    phi = -richardson_slope / (5.04e3)
    relative_error = abs(phi - 4.54) / 4.54

    print("\nTable-2 values")
    print("T / K:", " ".join(f"{value:.2f}" for value in temperatures))
    print("lg I / uA:", " ".join(f"{value:.4f}" for value in lg_i0_values))
    print("1/T / 1e-4 K^-1:", " ".join(f"{value * 1e4:.4f}" for value in inv_t))
    print("lg(I/T^2):", " ".join(f"{value:.4f}" for value in lg_i_over_t2))

    print("\nRichardson fit with x = 1/T")
    print(
        f"slope={richardson_slope:.8f}, intercept={richardson_intercept:.8f}, "
        f"R^2={richardson_r2:.6f}"
    )
    print("Richardson points:", " ".join(f"({x * 1e4:.4f},{y:.4f})" for x, y in zip(inv_t, lg_i_over_t2)))
    print(f"Plot form with x = 1e4/T: y = {richardson_slope / 1e4:.8f}x + {richardson_intercept:.8f}")
    print(f"phi = {phi:.8f} eV")
    print(f"relative error = {relative_error:.6%}")


if __name__ == "__main__":
    main()
