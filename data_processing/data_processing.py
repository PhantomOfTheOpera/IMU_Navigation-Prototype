from madjwick import MagwickFilter
import math
import numpy as np
import matplotlib.pyplot as plt


dt = 0.01
deg2rad = 180 / math.pi
rad_scaler = deg2rad * 800
kalman = 1

g = 9.83


def transform(a, b):
    a1, a2, a3, a4 = a
    b1, b2, b3, b4 = b

    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1

    return c1, c2, c3, c4


def process(path_data, path_result, path_figure):
    if type(path_data) == list:
        data = path_data
    else:
        with open(path_data) as f:
            data = [list(map(float, item.split())) for item in f.readlines()]


    m = MagwickFilter(dt)


    accel_x_native = []
    accel_y_native = []
    accel_z_native = []

    accel_x = []
    accel_y = []
    accel_z = []

    times = []

    x_vector = []
    y_vector = []
    z_vector = []

    for idx, item in enumerate(data):
        t, a_x, a_y, a_z, w_x, w_y, w_z, m_x, m_y, m_z = item
        # a_x, a_y, a_z = map(lambda x: int(x) / 1000, [a_x, a_y, a_z])
        # w_x, w_y, w_z =  map(lambda x: int(x) / rad_scaler, [w_x, w_y, w_z])

        m.filter_update(w_x, w_y, w_z, a_x, a_y, a_z)

        q1, q2, q3, q4 = m.SEq_1, m.SEq_2, m.SEq_3, m.SEq_4

        _, xx, xy, xz = transform(transform([q1, q2, q3, q4], [0, 1, 0, 0]), [q1, -q2, -q3, -q4])
        _, yx, yy, yz = transform(transform([q1, q2, q3, q4], [0, 0, 1, 0]), [q1, -q2, -q3, -q4])
        _, zx, zy, zz = transform(transform([q1, q2, q3, q4], [0, 0, 0, 1]), [q1, -q2, -q3, -q4])

        x_vector.append((xx, xy, xz))
        y_vector.append((yx, yy, yz))
        z_vector.append((zx, zy, zz))

        # _, ae_x, ae_y, ae_z = transform(transform([q1, q2, q3, q4], [0, a_x, a_y, a_z]), [q1, -q2, -q3, -q4])
        _, ae_x, ae_y, ae_z = 0, a_x, a_y, a_z

        ae_z -= g

        accel_x.append(ae_x)
        accel_y.append(ae_y)
        accel_z.append(ae_z)

        times.append(t)

        # if idx % 10 == 0:
            # print(*map(lambda x: round(x, 3), [deg2rad * an_x, deg2rad * an_y, deg2rad * an_z]))
            # print(*map(lambda x: round(x, 3), [ae_x, ae_y, ae_z]))
            # print(*map(lambda x: round(x, 3), [a_x, a_y, a_z]))

    r = 0.2
    # veloc_x = [0]
    veloc_x = [-2 * math.pi * r / 1]
    veloc_y = [0]
    veloc_z = [0]

    for i in range(len(data)):
        veloc_x.append(veloc_x[-1] + accel_x[i] * dt)
        veloc_y.append(veloc_y[-1] + accel_y[i] * dt)
        veloc_z.append(veloc_z[-1] + accel_z[i] * dt)

    veloc_x.pop(0)
    veloc_y.pop(0)
    veloc_z.pop(0)


    x = [0]
    y = [0]
    z = [0]

    for i in range(len(data)):
        x.append(x[-1] + veloc_x[i] * dt)
        y.append(y[-1] + veloc_y[i] * dt)
        z.append(z[-1] + veloc_z[i] * dt)

    x.pop(0)
    y.pop(0)
    z.pop(0)

    with open(path_result, encoding="utf-8", mode="w") as f:
        for i in range(len(data)):
            f.write(f"{x[i]} {y[i]} {z[i]} {x_vector[i][0]} {x_vector[i][1]} {x_vector[i][2]} {y_vector[i][0]} {y_vector[i][1]} {y_vector[i][2]} {z_vector[i][0]} {z_vector[i][1]} {z_vector[i][2]}\n")

    plt.subplot(3, 3, 1)
    plt.plot(times, accel_z, linewidth=1)
    plt.subplot(3, 3, 2)
    plt.plot(times, accel_y, linewidth=1)
    plt.subplot(3, 3, 3)
    plt.plot(times, accel_x, linewidth=1)
    plt.subplot(3, 3, 4)
    plt.plot(times, veloc_z, linewidth=1)
    plt.subplot(3, 3, 5)
    plt.plot(times, veloc_y, linewidth=1)
    plt.subplot(3, 3, 6)
    plt.plot(times, veloc_x, linewidth=1)
    plt.subplot(3, 3, 7)
    plt.plot(times, z, linewidth=1)
    plt.subplot(3, 3, 8)
    plt.plot(times, y, linewidth=1)
    plt.subplot(3, 3, 9)
    plt.plot(times, x, linewidth=1)

    print(abs(x[-1] - x[0]) / r)
    print(abs(y[-1] - y[0]) / r)
    print(abs(z[-1] - z[0]) / r)

def main():
    f = plt.figure()
    process("data1.txt", "angular1.txt", f)
    process("data2.txt", "angular2.txt", f)

    # data = combine()
    # process(data, "angular_combined.txt", f)
    plt.savefig("media/fig_no_magno.png", dpi=400)


def combine():
    with open("data1.txt") as f:
        data1 = [list(map(float, item.split())) for item in f.readlines()]
    with open("data2.txt") as f:
        data2 = [list(map(float, item.split())) for item in f.readlines()]
    
    def merge(x, y):
        ans = []
        for a, b in zip(x, y):
            ans.append((a + b) / 2)
        return ans

    data = list(map(merge, data1, data2))
    return data

f = plt.figure()
process("data.txt", "angular.txt", f)
plt.savefig("media/fig_pdg.png")
