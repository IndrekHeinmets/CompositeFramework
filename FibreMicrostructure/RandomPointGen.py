import matplotlib.pyplot as plt
from math import sqrt
from math import pi
import random

# Find fibre count based on volume fraction:
def findFibreCount(fibre_diameter, fibre_volFraction, RVE_size):
    total_vol = RVE_size**3
    single_fibre_vol = pi * ((fibre_diameter / 2)**2) * RVE_size
    total_fibre_vol = fibre_volFraction * total_vol
    fibre_count = round(total_fibre_vol / single_fibre_vol, 0)
    actual_volFraction = round((single_fibre_vol * fibre_count) / total_vol, 4)
    return fibre_count, actual_volFraction

# Random fibre position creation:
def randFibrePos(fibre_diameter, fibre_count, fibre_spacing_buffer, RVE_size):
    point_lst = []
    point_lst.append((random.randrange(-int(RVE_size / 2), int(RVE_size / 2)), random.randrange(-int(RVE_size / 2), int(RVE_size / 2))))

    while len(point_lst) < fibre_count:
        for c, point in enumerate(point_lst):
            x, y = random.randrange(-int(RVE_size / 2), int(RVE_size / 2)), random.randrange(-int(RVE_size / 2), int(RVE_size / 2))
            x1, y1 = point
            dx, dy = abs(x1 - x), abs(y1 - y)
            if (fibre_diameter / 2) + fibre_spacing_buffer < sqrt((dx**2) + (dy**2)):
                if len(point_lst) < fibre_count:
                    point_lst.append((x, y))
    return point_lst

if __name__ == '__main__':
    # Variables:
    fibre_diameter = 20.0
    fibre_volFraction = 0.35
    fibre_spacing_buffer = 2.0
    RVE_size = 6 * fibre_diameter

    fibre_count, actual_volFraction = findFibreCount(fibre_diameter, fibre_volFraction, RVE_size)
    point_lst = randFibrePos(fibre_diameter, fibre_count, fibre_spacing_buffer, RVE_size)

    print(f'Fibre count for a given fibre volume fraction of {fibre_volFraction}: {fibre_count}')
    print(f'With {fibre_count} fibres, the actual fibre volume fraction will be: {actual_volFraction}')
    print(f'Points: {point_lst}')

    x_lst = []
    y_lst = []
    for c, point in enumerate(point_lst):
        x_lst.append(point[0])
        y_lst.append(point[1])

w = 10
d = 70
plt.figure(figsize=(w, w), dpi=d)
plt.axis([-60, 60, -60, 60])
size = 2000

plt.scatter(x_lst, y_lst, s=size)
plt.show()

# Tee graph korda (oiged suurused tappidel)