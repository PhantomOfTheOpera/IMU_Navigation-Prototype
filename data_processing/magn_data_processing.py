from madgwick_filter import madgwick_magn_filter
import math
import numpy as np
import matplotlib.pyplot as plt


dt = 0.012
deg2rad = 180 / math.pi
rad_scaler = deg2rad * 10
kalman = 0.01

accel_z_dreif = 0
accel_y_dreif = 0
accel_x_dreif = 0

g = 993


def transform(a, b):
    a1, a2, a3, a4 = a
    b1, b2, b3, b4 = b

    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1

    return c1, c2, c3, c4


def process(path_data, path_result, f):
    with open(path_data) as f:
        data = [list(map(float, item.split())) for item in f.readlines()]


    accel_x_native = []
    accel_y_native = []
    accel_z_native = []

    accel_x = []
    accel_y = []
    accel_z = []

    times = []

    accel_x_opt = [0]
    accel_y_opt = [0]
    accel_z_opt = [0]

    x_vector = []
    y_vector = []
    z_vector = []
    SEq_1, SEq_2, SEq_3, SEq_4 = 1.0, 0.0, 0.0, 0.0


    for idx, item in enumerate(data):
        t, a_x, a_y, a_z, w_x, w_y, w_z, m_x, m_y, m_z = item
        w_x, w_y, w_z =  w_x / rad_scaler, w_y / rad_scaler, w_z / rad_scaler

        a_x -= accel_x_dreif
        a_y -= accel_y_dreif
        a_z -= accel_z_dreif
        m_x, m_y, m_z = 1, 1, 1

        SEq_1, SEq_2, SEq_3, SEq_4 = madgwick_magn_filter(SEq_1, SEq_2, SEq_3,
                                                        SEq_4, w_x, w_y, w_z,
                                                        a_x, a_y, a_z,
                                                        m_x, m_y, m_z)

        q1, q2, q3, q4 = SEq_1, SEq_2, SEq_3, SEq_4

        _, xx, xy, xz = transform(transform([q1, q2, q3, q4], [0, 1, 0, 0]), [q1, -q2, -q3, -q4])
        _, yx, yy, yz = transform(transform([q1, q2, q3, q4], [0, 0, 1, 0]), [q1, -q2, -q3, -q4])
        _, zx, zy, zz = transform(transform([q1, q2, q3, q4], [0, 0, 0, 1]), [q1, -q2, -q3, -q4])

        x_vector.append((xx, xy, xz))
        y_vector.append((yx, yy, yz))
        z_vector.append((zx, zy, zz))

        _, ae_x, ae_y, ae_z = transform(transform([q1, q2, q3, q4], [0, a_x, a_y, a_z]), [q1, -q2, -q3, -q4])

        ae_z -= g

        accel_x_opt.append((1 - kalman) * accel_x_opt[-1] + kalman * ae_x)
        accel_y_opt.append((1 - kalman) * accel_y_opt[-1] + kalman * ae_y)
        accel_z_opt.append((1 - kalman) * accel_z_opt[-1] + kalman * ae_z)

        accel_x.append(ae_x)
        accel_y.append(ae_y)
        accel_z.append(ae_z)

        accel_x_native.append(a_x)
        accel_y_native.append(a_y)
        accel_z_native.append(a_z)

        times.append(t / 1000)

        # if idx % 10 == 0:
            # print(*map(lambda x: round(x, 3), [deg2rad * an_x, deg2rad * an_y, deg2rad * an_z]))
            # print(*map(lambda x: round(x, 3), [ae_x, ae_y, ae_z]))
            # print(*map(lambda x: round(x, 3), [a_x, a_y, a_z]))

    accel_x_opt.pop(0)
    accel_y_opt.pop(0)
    accel_z_opt.pop(0)

    print(np.mean(np.array(accel_z)))
    print(np.mean(np.array(accel_y)))
    print(np.mean(np.array(accel_x)))

    print(np.mean(np.array(accel_z_native)))
    print(np.mean(np.array(accel_y_native)))
    print(np.mean(np.array(accel_x_native)))

    veloc_x = [0]
    veloc_y = [0]
    veloc_z = [0]

    for i in range(len(data)):
        veloc_x.append(veloc_x[-1] + accel_x_opt[i] * dt / 1000)
        veloc_y.append(veloc_y[-1] + accel_y_opt[i] * dt / 1000)
        veloc_z.append(veloc_z[-1] + accel_z_opt[i] * dt / 1000)

    veloc_x.pop(0)
    veloc_y.pop(0)
    veloc_z.pop(0)


    x = [0]
    y = [0]
    z = [0]

    for i in range(len(data)):
        x.append(x[-1] + veloc_x[i] * dt + accel_x[i] * dt**2 / 2)
        y.append(y[-1] + veloc_y[i] * dt + accel_y[i] * dt**2 / 2)
        z.append(z[-1] + veloc_z[i] * dt + accel_z[i] * dt**2 / 2)

    x.pop(0)
    y.pop(0)
    z.pop(0)

    with open(path_result, encoding="utf-8", mode="w") as f:
        for i in range(len(data)):
            f.write(f"{x[i]} {y[i]} {z[i]} {x_vector[i][0]} {x_vector[i][1]} {x_vector[i][2]} {y_vector[i][0]} {y_vector[i][1]} {y_vector[i][2]} {z_vector[i][0]} {z_vector[i][1]} {z_vector[i][2]}\n")

    plt.subplot(4, 3, 1)
    plt.plot(times, accel_z, linewidth=1)
    plt.subplot(4, 3, 2)
    plt.plot(times, accel_y, linewidth=1)
    plt.subplot(4, 3, 3)
    plt.plot(times, accel_x, linewidth=1)
    plt.subplot(4, 3, 4)
    plt.plot(times, accel_z_opt, linewidth=1)
    plt.subplot(4, 3, 7)
    plt.plot(times, veloc_z, linewidth=1)
    plt.subplot(4, 3, 5)
    plt.plot(times, accel_y_opt, linewidth=1)
    plt.subplot(4, 3, 8)
    plt.plot(times, veloc_y, linewidth=1)
    plt.subplot(4, 3, 6)
    plt.plot(times, accel_x_opt, linewidth=1)
    plt.subplot(4, 3, 9)
    plt.plot(times, veloc_x, linewidth=1)
    plt.subplot(4, 3, 10)
    plt.plot(times, z, linewidth=1)
    plt.subplot(4, 3, 11)
    plt.plot(times, y, linewidth=1)
    plt.subplot(4, 3, 12)
    plt.plot(times, x, linewidth=1)


f = plt.figure()
process("data1.txt", "angular1.txt", f)
process("data2.txt", "angular2.txt", f)
plt.savefig("media/fig_pdg.png")
