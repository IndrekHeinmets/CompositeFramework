from math import hypot
from math import sin
from math import pi


def arclength(sin_x, f, a, b, tol=1e-6):
    nsteps = 100
    oldlength = 1.0e20
    length = 1.0e10
    while abs(oldlength - length) >= tol:
        nsteps *= 2
        fx1 = f(sin_x, a)
        xdel = (b - a) / nsteps
        oldlength = length
        length = 0
        for i in range(1, nsteps + 1):
            fx0 = fx1
            fx1 = f(sin_x, (a + i * (b - a) / nsteps))
            length += hypot(xdel, fx1 - fx0)
    return length


def ellipse_surfaceArea(width, heigth):
    return pi * (width / 2) * (heigth / 2)


def fibre_volume(length, surfaceArea, fibre_count):
    return length * surfaceArea * fibre_count


def matrix_volume(width, height, fiber_vol):
    return (width * width * height) - fiber_vol


def find_volume_fraction(fiber_vol, matrix_vol):
    total_vol = fiber_vol + matrix_vol
    vf_fibres = round(fiber_vol / total_vol, 4)
    vf_matrix = round(matrix_vol / total_vol, 4)
    return vf_fibres, vf_matrix


def run(sin_x, f, x_beg, x_end, e_width, e_height, b_width, b_height, fibre_count):
    arc_len = arclength(sin_x, f, x_beg, x_end, 1e-10)
    ellipse_surf = ellipse_surfaceArea(e_width, e_height)
    fiber_vol = fibre_volume(arc_len, ellipse_surf, fibre_count)
    matrix_vol = matrix_volume(b_width, b_height, fiber_vol)
    return find_volume_fraction(fiber_vol, matrix_vol)


def f(sin_x, x):
    return sin(sin_x * x)


if __name__ == '__main__':
    ############################# VARIABLES ###################################
    # Resin block:
    b_width = 38.0
    b_height = 4.0

    # Weave spline:
    sin_x = 0.5
    x_beg, x_end = 0.0, b_width
    fibre_count = 12

    # Ellipse cs:
    e_width = 4.5
    e_height = 1.2

    VolFraction_Fibres, VolFraction_Matrix = run(sin_x, f, x_beg, x_end, e_width, e_height, b_width, b_height, fibre_count)
    print(f"Volume Fraction of CF Fibers: {VolFraction_Fibres * 100}%")
    print(f"Volume Fraction of Resin Matrix: {VolFraction_Matrix * 100}%")
