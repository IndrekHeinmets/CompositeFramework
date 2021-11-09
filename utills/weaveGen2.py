from math import sin
from math import pi
import matplotlib.pyplot as plt


def find_spline_nodes_l(sin_x, step, pi_len, overlap_pi_len, sc):
    x_points, y_points = [], []
    points = []
    i, offset = 0, 0

    while i <= int((pi_len * pi) / step):
        x = step * i
        i += 1

        y_b = (sin(sin_x * (x - step))) / sc
        y = (sin(sin_x * x)) / sc
        y_a = (sin(sin_x * (x + step))) / sc
        x += offset

        if y_b < y < y_a or y_b > y > y_a:
            points.append((x, y))
            x_points.append(x)
            y_points.append(y)

        else:
            j = 0
            while j <= int((overlap_pi_len * pi) / step):
                j += 1
                x += (step * j)
                offset += (step * j)
                points.append((x, y))
                x_points.append(x)
                y_points.append(y)


    print(len(points))
    print(len(x_points))
    print(len(y_points))

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
    overlap_pi_len = (period * 24) / pi

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

    x, y, p = find_spline_nodes_l((sin_x * sc), (step / sc), (pi_len / sc), (overlap_pi_len / sc), sc)
    # print(p)
    # print(len(p))

    plt.plot(x, y)
    plt.show()
