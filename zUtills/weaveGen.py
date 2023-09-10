from math import sin
from math import pi
import matplotlib.pyplot as plt


def add_straight(x, y, overlap_len, step, points, x_points, y_points, offset):
    for i in range(int(overlap_len / step)):
        x += step
        offset += step
        points.append((x, y))
        x_points.append(x)
        y_points.append(y)

    return x, offset, points, x_points, y_points


def find_spline_nodes(sin_x, step, pi_len, overlap_len, sc):
    x_points, y_points = [], []
    points = []
    offset = 0

    for i in range(int((pi_len * pi) / step)):
        x = step * i
        y_b = sin(sin_x * (x - step)) / sc
        y = sin(sin_x * x) / sc
        y_a = sin(sin_x * (x + step)) / sc
        x += offset

        if y_b < y < y_a or y_b > y > y_a:
            points.append((x, y))
            x_points.append(x)
            y_points.append(y)

        else:
            x, offset, points, x_points, y_points = add_straight(x, y, overlap_len, step, points, x_points, y_points, offset)

    return x_points, y_points, points


if __name__ == '__main__':
    ############################# VARIABLES ###################################
    # Scale (m -> mm):
    sc = 1000

    # Sin curve:
    sin_x = 0.5
    step = 0.01
    pi_len = 24.0
    period = pi / (sin_x * sc)

    # Overlap
    overlap_len = 3 * period

    # Ellipse cs:
    e_width = 4.5
    e_height = 0.6

    # Resin block:
    b_width = (pi_len * pi)
    b_height = 4.0

    # Fiber prop:
    f_name = 'Carbon Fiber'
    f_YsM = 228000000000.0
    f_PsR = 0.28

    # Matrix prop:
    m_name = 'Epoxy Resin'
    m_YsM = 38000000000.0
    m_PsR = 0.35

    # Mesh density:
    md = 0.5
    ###########################################################################

    x, y, p = find_spline_nodes((sin_x * sc), (step / sc), (pi_len / sc), overlap_len, sc)
    plt.plot(x, y)
    plt.show()
