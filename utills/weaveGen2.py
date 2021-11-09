from math import sin
from math import pi
import matplotlib.pyplot as plt


def find_spline_nodes(sin_x, step, pi_len, sc):
    x_points = []
    y_points = []
    points = []
    len_overlap = 41

    # Fill x values:
    for i in range(0, int((pi_len * pi) / step)):
        x = step * i
        x_points.append(x)

    # Fill y values:
    for x in x_points:
        y = sin(sin_x * x) / sc
        y_points.append(y)

    for i in range(len(y_points)):
        try:
            if y_points[i - 1] < y_points[i] < y_points[i + 1] or y_points[i - 1] > y_points[i] > y_points[i + 1]:
                points.append((x_points[i], y_points[i]))
            else:
                for j in range(0, int(len_overlap / step)):
                    x = step * j
                    points.append((x, y_points[i]))

        except IndexError:
            points.append((x_points[i], y_points[i]))


    points = tuple(points)

    return x_points, y_points, points



if __name__ == '__main__':
    ############################# VARIABLES ###################################
    # Scale (m -> mm):
    sc = 1000

    len_fibre = 75
    step = 0.05
    sin_x = 0.5
    pi_len = len_fibre // pi
    period = pi / (sin_x * sc)


    # Ellipse cs:
    e_width = 4.5
    e_height = 0.6

    # Resin block:
    b_width = len_fibre
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

    x, y, p = find_spline_nodes((sin_x * sc), (step / sc), (pi_len / sc), sc)
    print(p)
    print(len(p))

    plt.plot(x, y)
    plt.show()
