import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
from math import sqrt
from math import pi
import random

# Find fibre count based on volume fraction:


def findFibreCount():
    total_vol = RVE_size**3
    single_fibre_vol = pi * ((fibre_diameter / 2)**2) * RVE_size
    total_fibre_vol = fibre_volFraction * total_vol
    fibre_count = round(total_fibre_vol / single_fibre_vol, 0)
    actual_volFraction = round((single_fibre_vol * fibre_count) / total_vol, 4)
    return fibre_count, actual_volFraction

# Check for fibre overlap:


def checkFibreCol(edge_lst, point_lst, x, y):
    valid = True
    for point in point_lst:
        x1, y1 = point
        dx, dy = abs(x1 - x), abs(y1 - y)
        if fibre_diameter + fibre_spacing_buffer > sqrt((dx ** 2) + (dy ** 2)):
            valid = False
    for point in edge_lst:
        x1, y1 = point
        dx, dy = abs(x1 - x), abs(y1 - y)
        if fibre_diameter + fibre_spacing_buffer > sqrt((dx ** 2) + (dy ** 2)):
            valid = False
    return valid

# Generate corresponding half fibre pairs:


def handleHalfFibres(edge_lst, point_lst, x, y, edge_bound):
    # Corners:
    if x > edge_bound and y > edge_bound:
        x1 = x - RVE_size
        valid1 = checkFibreCol(edge_lst, point_lst, x1, y)
        y2 = y - RVE_size
        valid2 = checkFibreCol(edge_lst, point_lst, x, y2)
        x3, y3 = x - RVE_size, y - RVE_size
        valid3 = checkFibreCol(edge_lst, point_lst, x3, y3)
        if valid1 and valid2 and valid3:
            point_lst.append((x, y))
            edge_lst.append((x1, y))
            edge_lst.append((x, y2))
            edge_lst.append((x3, y3))
    elif x > edge_bound and y < -edge_bound:
        x1 = x - RVE_size
        valid1 = checkFibreCol(edge_lst, point_lst, x1, y)
        y2 = y + RVE_size
        valid2 = checkFibreCol(edge_lst, point_lst, x, y2)
        x3, y3 = x - RVE_size, y + RVE_size
        valid3 = checkFibreCol(edge_lst, point_lst, x3, y3)
        if valid1 and valid2 and valid3:
            point_lst.append((x, y))
            edge_lst.append((x1, y))
            edge_lst.append((x, y2))
            edge_lst.append((x3, y3))
    elif x < -edge_bound and y < -edge_bound:
        x1 = x + RVE_size
        valid1 = checkFibreCol(edge_lst, point_lst, x1, y)
        y2 = y + RVE_size
        valid2 = checkFibreCol(edge_lst, point_lst, x, y2)
        x3, y3 = x + RVE_size, y + RVE_size
        valid3 = checkFibreCol(edge_lst, point_lst, x3, y3)
        if valid1 and valid2 and valid3:
            point_lst.append((x, y))
            edge_lst.append((x1, y))
            edge_lst.append((x, y2))
            edge_lst.append((x3, y3))
    elif x < -edge_bound and y > edge_bound:
        x1 = x + RVE_size
        valid1 = checkFibreCol(edge_lst, point_lst, x1, y)
        y2 = y - RVE_size
        valid2 = checkFibreCol(edge_lst, point_lst, x, y2)
        x3, y3 = x + RVE_size, y - RVE_size
        valid3 = checkFibreCol(edge_lst, point_lst, x3, y3)
        if valid1 and valid2 and valid3:
            point_lst.append((x, y))
            edge_lst.append((x1, y))
            edge_lst.append((x, y2))
            edge_lst.append((x3, y3))
    # Edges:
    elif x > edge_bound:
        x1 = x - RVE_size
        valid = checkFibreCol(edge_lst, point_lst, x1, y)
        if valid:
            point_lst.append((x, y))
            edge_lst.append((x1, y))
    elif y > edge_bound:
        y1 = y - RVE_size
        valid = checkFibreCol(edge_lst, point_lst, x, y1)
        if valid:
            point_lst.append((x, y))
            edge_lst.append((x, y1))
    elif x < -edge_bound:
        x1 = x + RVE_size
        valid = checkFibreCol(edge_lst, point_lst, x1, y)
        if valid:
            point_lst.append((x, y))
            edge_lst.append((x1, y))
    elif y < -edge_bound:
        y1 = y + RVE_size
        valid = checkFibreCol(edge_lst, point_lst, x, y1)
        if valid:
            point_lst.append((x, y))
            edge_lst.append((x, y1))
    return edge_lst, point_lst

# Random fibre position creation:


def randFibrePos():
    edge_lst = []
    point_lst = []
    edge_bound = (RVE_size / 2) - (fibre_diameter / 2)

    while len(point_lst) < fibre_count:
        x, y = random.randrange(-int(RVE_size / 2), int(RVE_size / 2)), random.randrange(-int(RVE_size / 2), int(RVE_size / 2))
        valid = checkFibreCol(edge_lst, point_lst, x, y)
        if valid:
            if x > edge_bound or y > edge_bound or x < -edge_bound or y < -edge_bound:
                edge_lst, point_lst = handleHalfFibres(edge_lst, point_lst, x, y, edge_bound)
            else:
                point_lst.append((x, y))
    for point in edge_lst:
        point_lst.append(point)
    return point_lst


if __name__ == '__main__':
    # Variables:
    fibre_diameter = 20.0
    fibre_volFraction = 0.35
    fibre_spacing_buffer = fibre_diameter / 7
    RVE_size = 6 * fibre_diameter

    fibre_count, actual_volFraction = findFibreCount()
    point_lst = randFibrePos()

    print(f'Fibre count for a given fibre volume fraction of {fibre_volFraction}: {fibre_count}')
    print(f'With {fibre_count} fibres, the actual fibre volume fraction will be: {actual_volFraction}')
    print(f'Points: {point_lst}')

    x_lst, y_lst = [], []
    for point in point_lst:
        x_lst.append(point[0])
        y_lst.append(point[1])

    # # 3D PLOTTING
    # def z_function(x, y):
    #     return np.sin(np.sqrt(x ** 2 + y ** 2))

    # X, Y = np.meshgrid(x_lst, y_lst)
    # Z = z_function(X, Y)
    # fig = plt.figure()
    # ax = plt.axes(projection="3d")
    # ax.plot_wireframe(X, Y, Z, color='green')
    # ax.set_xlabel('x')
    # ax.set_ylabel('y')
    # ax.set_zlabel('z')
    # plt.show()s

    plt.figure(figsize=(10, 10), dpi=70)
    plt.axis([-60, 60, -60, 60])
    plt.scatter(x_lst, y_lst, s=7000)
    plt.show()
