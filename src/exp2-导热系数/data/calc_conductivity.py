"""Reproduce the conductivity calculation for exp2."""

from math import pi


T1_STEADY = [79.6, 79.6, 79.6, 79.6, 79.5, 79.5, 79.5, 79.5, 79.5, 79.5]
T2_STEADY = [57.8, 58.1, 58.4, 58.6, 58.8, 59.0, 59.2, 59.3, 59.4, 59.4]

COOLING_DATA = [
    (30, 68.4),
    (60, 66.9),
    (90, 65.6),
    (120, 64.2),
    (150, 63.0),
    (180, 61.7),
    (210, 60.6),
    (240, 59.5),
    (270, 58.5),
    (300, 57.5),
    (330, 56.5),
    (360, 55.6),
    (390, 54.6),
    (420, 54.6),
    (450, 53.7),
    (480, 52.8),
    (510, 51.2),
    (540, 50.4),
    (570, 49.7),
    (600, 49.1),
]

MASS_KG = 0.823
H_P_M = 0.007
H_B_M = 0.005
R_P_M = 0.065
R_B_M = 0.065
COPPER_C = 385.0
def mean(values):
    return sum(values) / len(values)


def linear_regression(points):
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    x_bar = mean(xs)
    y_bar = mean(ys)
    slope = sum((x - x_bar) * (y - y_bar) for x, y in points) / sum(
        (x - x_bar) ** 2 for x in xs
    )
    intercept = y_bar - slope * x_bar
    return slope, intercept


def fit_hyperbolic_curve(points, target_temp):
    """Fit T = a / (t + b) + c by searching c and linearizing 1 / (T - c)."""
    times = [t for t, _ in points]
    temps = [temp for _, temp in points]
    min_temp = min(temps)

    def objective(c_value):
        if any(temp - c_value <= 0 for temp in temps):
            return None
        transformed = [(t, 1.0 / (temp - c_value)) for t, temp in points]
        slope, intercept = linear_regression(transformed)
        if slope <= 0:
            return None
        a_value = 1.0 / slope
        b_value = intercept / slope
        residual = sum(
            (temp - (a_value / (t + b_value) + c_value)) ** 2
            for t, temp in points
        )
        return residual, a_value, b_value

    best = None
    c_value = -20.0
    while c_value < min_temp - 0.001:
        candidate = objective(c_value)
        if candidate is not None and (best is None or candidate[0] < best[0]):
            best = (candidate[0], c_value, candidate[1], candidate[2])
        c_value += 0.001

    _, coarse_c, _, _ = best
    best = None
    c_value = coarse_c - 0.01
    while c_value <= coarse_c + 0.01:
        candidate = objective(c_value)
        if candidate is not None and (best is None or candidate[0] < best[0]):
            best = (candidate[0], c_value, candidate[1], candidate[2])
        c_value += 0.00001

    _, c_value, a_value, b_value = best
    time_at_target_temp = a_value / (target_temp - c_value) - b_value
    cooling_rate = -a_value / (time_at_target_temp + b_value) ** 2
    predicted = [a_value / (t + b_value) + c_value for t in times]
    temp_bar = mean(temps)
    r_squared = 1.0 - sum(
        (temp - pred) ** 2 for temp, pred in zip(temps, predicted)
    ) / sum((temp - temp_bar) ** 2 for temp in temps)
    return a_value, b_value, c_value, time_at_target_temp, cooling_rate, r_squared


def main():
    t1_avg = mean(T1_STEADY)
    t2_avg = mean(T2_STEADY)
    a_value, b_value, c_value, t_at_t2, cooling_rate, r_squared = fit_hyperbolic_curve(
        COOLING_DATA, t2_avg
    )

    conductivity = (
        -MASS_KG
        * COPPER_C
        * (R_P_M + 2 * H_P_M)
        / (2 * R_P_M + 2 * H_P_M)
        * (1 / (pi * R_B_M**2))
        * (H_B_M / (t1_avg - t2_avg))
        * cooling_rate
    )

    print(f"T1_avg = {t1_avg:.4f} C")
    print(f"T2_avg = {t2_avg:.4f} C")
    print(f"T(t) = {a_value:.6f} / (t + {b_value:.6f}) + {c_value:.6f}")
    print(f"R^2 = {r_squared:.6f}")
    print(f"t(T2_avg) = {t_at_t2:.4f} s")
    print(f"dT/dt|T=T2 = {cooling_rate:.6f} C/s")
    print(f"lambda = {conductivity:.6f} W/(m*K)")


if __name__ == "__main__":
    main()
