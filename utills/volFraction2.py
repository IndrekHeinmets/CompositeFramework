from math import hypot
from math import sin
from math import pi
# StackOverflow: https://stackoverflow.com/questions/46098157/how-to-calculate-the-length-of-a-curve-of-a-math-function


def arclength(sin_x, f, a, b, tol=1e-6):
    nsteps = 100  # number of steps to compute
    oldlength = 1.0e20
    length = 1.0e10
    while abs(oldlength - length) >= tol:
        nsteps *= 2
        fx1 = f(sin_x, a)
        xdel = (b - a) / nsteps  # space between x-values
        oldlength = length
        length = 0
        for i in range(1, nsteps + 1):
            fx0 = fx1  # previous function value
            fx1 = f(sin_x, (a + i * (b - a) / nsteps))  # new function value
            length += hypot(xdel, fx1 - fx0)  # length of small line segment
    return length


def ellipse_surfaceArea(width, heigth):
    return pi * (width / 2) * (heigth / 2)


def fibre_volume(length, surfaceArea, fibre_count):
    return length * surfaceArea * fibre_count


def matrix_volume(width, height, fiber_vol):
    return (width * width * height) - fiber_vol


def find_volume_fraction(fiber_vol, matrix_vol):
    total_vol = fiber_vol + matrix_vol
    vf_fibres = fiber_vol / total_vol
    vf_matrix = matrix_vol / total_vol
    print(vf_fibres)
    print(vf_matrix)
    print(fiber_vol)
    print(matrix_vol)
    print(total_vol)
    return vf_fibres, vf_matrix


def run(sin_x, f, x_beg, x_end, e_width, e_height, b_width, b_height, fibre_count):
    arc_len = arclength(sin_x, f, x_beg, x_end, 1e-10)
    ellipse_surf = ellipse_surfaceArea(e_width, e_height)
    fiber_vol = fibre_volume(arc_len, ellipse_surf, fibre_count)
    matrix_vol = matrix_volume(b_width, b_height, fiber_vol)
    return find_volume_fraction(fiber_vol, matrix_vol)


def f(sin_x, x):
    return sin(sin_x * x)

########################################################
# Scale
sc = 1000

# Resin block:
b_width = 24.0
b_height = 4.0

# Weave spline:
sin_x = 0.5
x_beg, x_end = 0.0, b_width
fibre_count = 6

# Ellipse cs:
e_width = 4.5
e_height = 0.6

VolFraction_Fibres, VolFraction_Matrix = run((sin_x * sc), f, (x_beg / sc), (x_end / sc), (e_width / sc), (e_height / sc), (b_width / sc), (b_height / sc), fibre_count)
# print(f"Volume Fraction of CF Fibers: {VolFraction_Fibres}")
# print(f"Volume Fraction of Resin Matrix: {VolFraction_Matrix}")
