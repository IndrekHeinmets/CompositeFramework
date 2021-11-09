from math import sin
from math import pi
import matplotlib.pyplot as plt


def find_spline_nodes(sin_x, step, pi_len, sc):
    x_points = []
    y_points = []
    points = []
    length = 0
    x_ap = 0
    y_ap = 0
    i = 0
    offset = 0

    while i <= int((pi_len * pi) / step):

        x = step * i
        i += 1

        y_b = (sin(sin_x * (x - step))) / sc
        y = (sin(sin_x * x)) / sc
        y_a = (sin(sin_x * (x + step))) / sc
        x += offset

        if y_b < y < y_a or y_b > y > y_a:
            x_ap = x
            y_ap = y

        else:
            for j in range(0, length):
                x += (step * j)
                offset += (step * j)
                x_ap = x
                y_ap = y

        x_points.append(x_ap)
        y_points.append(y_ap)
        points.append((x, y))

    return x_points, y_points, points


if __name__ == '__main__':
    sc = 1000
    sin_x = 0.5
    step = 0.01
    pi_len = 12.0

    x_points, y_points, points = find_spline_nodes((sin_x * sc), (step / sc), (pi_len / sc), sc)

    plt.plot(x_points, y_points)
    plt.show()
