def find_sin_nodes(sin_x, step, pi_len):
    points1 = []
    points2 = []

    for i in range(0, int((pi_len * pi) / step)):
        x = step * i
        y1 = sin(sin_x * x)
        y2 = sin((sin_x * x) + pi)
        points1.append((x, y1))
        points2.append((x, y2))

    points1 = tuple(points1)
    points2 = tuple(points2)

    return points1, points2


if __name__ == '__main__':
    sin_x = 0.5
    step = 0.01
    pi_len = 24.0
    points1, points2 = find_sin_nodes(sin_x, step, pi_len)
    print(len(points1, points2))
    print(points1)
    print(points2)
