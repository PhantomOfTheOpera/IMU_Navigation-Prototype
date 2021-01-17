import serial
import time
import threading


def read_data_stm32_vcp(n, path, filename):
    ctr = 0
    lines = []

    with serial.Serial(path) as ser:
        try:
            while 1:
                s = str(ser.readline())
                ctr += 1
                tm, a_x, a_y, a_z, m_x, m_y, m_z, w_x, w_y, w_z = s[2:-3].split(";")
                # w_x, w_y, w_z, m_x, m_y, m_z = map(lambda x: int(x) / 1600, [w_x, w_y, w_z, m_x, m_y, m_z])

                if ctr == 1:
                    start = int(time.time() * 1000)
                    tm0 = tm

                real_time = start + int(tm) - int(tm0)

                lines.append(f"{real_time} {a_x} {a_y} {a_z} {w_x} {w_y} {w_z} {m_x} {m_y} {m_z}\n")

                if ctr % 20 == 0:
                    print(path, tm, a_x, a_y, a_z, w_x, w_y, w_z, m_x, m_y, m_z)

                if ctr == n:
                    raise KeyboardInterrupt

        except KeyboardInterrupt:
            with open(f"{filename}.txt", mode="w") as f:
                f.writelines(lines)

x = threading.Thread(target=read_data_stm32_vcp, args=(2 * 10**3, "/dev/ttyACM0", "data1"))
x.start()
y = threading.Thread(target=read_data_stm32_vcp, args=(2 * 10**3, "/dev/ttyACM1", "data2"))
y.start()