def bresenham_algorithm(x0, y0, x1, y1):
    # Różnica na x i różnica na y
    dx = x1 - x0
    dy = y1 - y0

    # Z jakim znakiem występują różnice?
    x_sign = 1 if dx > 0 else -1
    y_sign = 1 if dy > 0 else -1

    # Interesują nas wartości bezwzględne
    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        # Jeśli różnica na x jest większa niż różnica na y
        xx, xy, yx, yy = x_sign, 0, 0, y_sign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, y_sign, x_sign, 0

    # Zmienna decyzyjna
    D = 2 * dy - dx
    y = 0

    # Obliczanie kolejnych punktów
    for x in range(dx + 1):
        yield x0 + x * xx + y * yx, y0 + x * xy + y * yy
        if D >= 0:
            y += 1
            D -= 2 * dx
        D += 2 * dy
