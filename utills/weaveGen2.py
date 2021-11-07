from math import sin
from math import pi
import matplotlib.pyplot as plt
import numpy as np


def find_spline_nodes(len_fibre, step):
    x_points = []
    y_points = []

    # Fill xPoints
    for c, x in enumerate(0, (len_fibre / step)):
        x_points.append(x + (c * step))
        print(x_points)
        np

    return 0
    # points = []
    # length = 36
    # x_ap = 0
    # y_ap = 0
    # i = 0
    # offset = 0
    #
    # while i <= int((pi_len * pi) / step):
    #
    #     x = step * i
    #     i += 1
    #
    #
    #     y_b = (sin(sin_x * (x - step))) / sc
    #     y = (sin(sin_x * x)) / sc
    #     y_a = (sin(sin_x * (x + step))) / sc
    #     x += offset
    #
    #     if y_b < y < y_a or y_b > y > y_a:
    #         x_ap = x
    #         y_ap = y
    #
    #     else:
    #         for j in range(0, length):
    #             x += (step * j)
    #             offset += (step * j)
    #             x_ap = x
    #             y_ap = y
    #
    #     x_points.append(x_ap)
    #     y_points.append(y_ap)
    #     points.append((x, y))
    #
    # return x_points, y_points, points


if __name__ == '__main__':
    ############################# VARIABLES ###################################
    # Scale (m -> mm):
    sc = 1000

    LEN_FIBRE = 15
    STEP = 0.01

    # # Sin curve:
    # sin_x = 0.5
    # step = 0.01
    # pi_len = 24.0
    # period = pi / (sin_x * sc)
    #
    # # Ellipse cs:
    # e_width = 4.5
    # e_height = 0.6
    #
    # # Resin block:
    # b_width = (pi_len * pi)
    # b_height = 4.0

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

    x_points, y_points, points = find_spline_nodes(LEN_FIBRE, STEP)

    plt.plot(x_points, y_points)
    plt.show()
