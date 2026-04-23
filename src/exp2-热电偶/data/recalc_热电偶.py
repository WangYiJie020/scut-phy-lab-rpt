from math import sqrt


TEMPERATURES = [40, 50, 60, 70, 80, 90, 100]
EMFS_MV = [1.2, 1.4, 1.7, 2.0, 2.3, 2.6, 2.8]


def linear_fit(xs, ys):
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    s_xx = sum((x - x_mean) ** 2 for x in xs)
    s_yy = sum((y - y_mean) ** 2 for y in ys)
    s_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))

    slope = s_xy / s_xx
    intercept = y_mean - slope * x_mean
    predictions = [slope * x + intercept for x in xs]
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, predictions))
    r = s_xy / sqrt(s_xx * s_yy)
    r_squared = 1 - ss_res / s_yy
    return slope, intercept, r, r_squared, predictions


def main():
    slope, intercept, r, r_squared, predictions = linear_fit(
        TEMPERATURES,
        EMFS_MV,
    )

    print(f"slope = {slope:.12f} mV/°C")
    print(f"intercept = {intercept:.12f} mV")
    print(f"r = {r:.12f}")
    print(f"R^2 = {r_squared:.12f}")
    print(f"inverse: T = {1 / slope:.6f} E {(-intercept / slope):+.6f}")
    print("residuals (mV):")
    for temperature, emf, prediction in zip(TEMPERATURES, EMFS_MV, predictions):
        residual = emf - prediction
        print(
            f"  T={temperature:>3} °C, "
            f"E={emf:.1f} mV, "
            f"E_fit={prediction:.6f} mV, "
            f"delta={residual:+.6f} mV"
        )


if __name__ == "__main__":
    main()
