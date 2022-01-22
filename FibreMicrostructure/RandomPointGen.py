
fibre_diameter = 20
fibre_count = 16
fibre_spacing_buffer = 2
RVE_size = 6 * fibre_diameter

# Random fibre position creation:
point_lst = []
for i in range(fibre_count):
    x = random.randrange(-(RVE_size / 2), (RVE_size / 2))
    y = random.randrange(-(RVE_size / 2), (RVE_size / 2))
    point_lst.append((x, y))

    for c, point in enumerate(point_lst):
        x1, y1 = point_lst[c]
        dx, dy = abs(x1 - x), abs(y1 - y)
        if ((fibre_diameter / 2) + fibre_spacing_buffer) <= (sqrt((dx**2) + (dy**2))):
            a.Instance(name='Fibre-' + str(i + 1), part=p, dependent=ON)
            a.translate(instanceList=('Fibre-' + str(i + 1), ), vector=(x, y, 0.0))
