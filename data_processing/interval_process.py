def process(filename):
    lines = []
    with open(filename, encoding="utf-8", mode="r") as f:
        data = f.readlines()
        for idx, item in enumerate(data):
            if idx == len(data) - 1:
                break

            t, a_x, a_y, a_z, w_x, w_y, w_z = item.split()
            a_x, a_y, a_z, w_x, w_y, w_z = map(int, [a_x, a_y, a_z, w_x, w_y, w_z])
            t = int(float(t) * 1000)

            t1, a_x1, a_y1, a_z1, w_x1, w_y1, w_z1 = data[idx + 1].split()
            a_x1, a_y1, a_z1, w_x1, w_y1, w_z1 = map(int, [a_x1, a_y1, a_z1, w_x1, w_y1, w_z1])
            t1 = int(float(t1) * 1000)
            num = (t1 - t) // 25

            for i in range(num):
                t2 = t + i * (t1 - t) // num
                a_x2 = a_x + i * (a_x1 - a_x) / num 
                a_y2 = a_y + i * (a_y1 - a_y) / num 
                a_z2 = a_z + i * (a_z1 - a_z) / num 
                w_x2 = w_x + i * (w_x1 - w_x) / num 
                w_y2 = w_y + i * (w_y1 - w_y) / num 
                w_z2 = w_z + i * (w_z1 - w_z) / num

                a_x2, a_y2, a_z2, w_x2, w_y2, w_z2 = map(lambda x: round(x, 3), [a_x2, a_y2, a_z2, w_x2, w_y2, w_z2])

                lines.append(f"{t2} {a_x2} {a_y2} {a_z2} {w_x2} {w_y2} {w_z2}\n")

    with open(filename, encoding="utf-8", mode="w") as f:
        f.writelines(lines[::160])
