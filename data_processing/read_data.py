#!/usr/bin/env python3.6

import argparse
import struct
import logging
import datetime
from bluepy import btle
import binascii
import json
import time
from interval_process import process

import sys
sys.path.insert(0, "/usr/lib/python3/dist-packages")
import gatt

time.sleep(2)

ctr = 0
limit = 3000
lines = []


def transform(a, b):
    a1, a2, a3, a4 = a
    b1, b2, b3, b4 = b

    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1

    return c1, c2, c3, c4


def to_hex(d, by=16, separator_byte='-', separator_line='\n'):
    ret = []
    for j in range(len(d) // by + 1):
        line = binascii.hexlify(d[j * by:j * by + by]).decode()
        ret.append(separator_byte.join(["".join(b) for b in zip(line[::2], line[1::2])]))
    return ret if separator_line is None else separator_line.join(ret)


class BinaryJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            try:
                return obj.decode()
            except Exception as e:
                return obj.__str__()


class DeviceSeekerManager(gatt.DeviceManager):
    discovered_mac_address = None
    _search_for_name = None
    _discovered_devices = {}

    def __init__(self, search_for_name, *args, **kwargs):
        self._search_for_name = search_for_name
        super(DeviceSeekerManager, self).__init__(*args, **kwargs)

    def device_discovered(self, device):
        if device.mac_address not in self._discovered_devices:
            if device.alias() == self._search_for_name:
                logging.info("Discovered device [%s] %s" % (device.mac_address, device.alias()))
                self.discovered_mac_address = device.mac_address.upper()
                self.stop_discovery()
                self.stop()
            else:
                self._discovered_devices[device.mac_address] = datetime.datetime.now()
                logging.debug("Skipping Discovered [%s] %s" % (device.mac_address, device.alias()))


class Characteristic:
    handle = None
    prev_up = None
    records = []

    def ts(self, ind):
        return self.records[ind][0]

    def on_data(self, data):
        uptime = struct.unpack('I', data[0:4])[0]
        logging.info('uptime %s', uptime)
        accelerations = [struct.unpack('hhh', data[i:i + 6]) for i in range(4, len(data), 6)]
        logging.debug('%s records received', len(accelerations))

        if self.prev_up is not None:
            time_interval = (uptime - self.prev_up)/len(accelerations)
            for i, a in enumerate(accelerations):
                # print('!', i, time_interval, a)
                self.records.append((self.prev_up + time_interval*(i+1), a[0], a[1], a[2]))
                logging.info(self.records[-1])
                # print(f"{self.records[-1][0]}, {self.records[-1][1]}, {self.records[-1][2]:d}, {self.records[-1][3]}")
                while len(self.records) > 999:
                    self.records.pop()

        self.prev_up = uptime


class ActivityTracker:
    device = None
    device_addr = None
    _buffer = []
    counter = 0
    # _buffer_backup = None
    on_data = None
    data_chunk_size = None

    characteristics = {
        '25810102-2e23-afea-11f6-1b7082c0e8e9': Characteristic(),
        '25810103-2e23-afea-11f6-1b7082c0e8e9': Characteristic()
    }

    keys = list(characteristics.keys())

    def __init__(self, device_addr):
        self.device_addr = device_addr

    @staticmethod
    def _discover_address_by_name(device_name, adapter_name='hci0'):
        manager = DeviceSeekerManager(device_name, adapter_name=adapter_name)
        manager.start_discovery()
        manager.run()
        return manager.discovered_mac_address

    def sync_characteristics(self):

        no_data = False
        while not no_data:
            best_indexes = {c_uuid: 0 for c_uuid in self.keys}
            if len(self.keys) == 1 and len(self.characteristics[self.keys[0]].records) == 0:
                no_data = True
                break
            for inum, c_uuid in enumerate(self.keys):
                if inum == 0:
                    continue

                uid1 = self.keys[inum - 1]
                uid2 = c_uuid

                cr1 = self.characteristics[uid1]
                cr2 = self.characteristics[uid2]


                if len(cr1.records) == 0 or len(cr2.records) == 0:
                    no_data = True
                    break

                ts1 = cr1.ts(best_indexes[uid1])
                ts2 = cr2.ts(best_indexes[uid2])

                if ts1 < ts2:
                    if best_indexes[uid2] != 0 and abs(ts1 - ts2) > abs(ts1 - cr2.ts(best_indexes[uid2]-1)):
                        best_indexes[uid2] -= 1
                    elif best_indexes[uid1] != len(cr1.records) - 1 and abs(ts1 - ts2) > abs(ts2 - cr1.ts(best_indexes[uid1]+1)):
                        best_indexes[uid1] += 1
                else: #ts1>ts2
                    if best_indexes[uid1] != 0 and abs(ts1 - ts2) > abs(ts2 - cr1.ts(best_indexes[uid1] - 1)):
                        best_indexes[uid1] -= 1
                    elif best_indexes[uid2] != len(cr2.records) - 1 and abs(ts1 - ts2) > abs(
                            ts1 - cr2.ts(best_indexes[uid2] + 1)):
                        best_indexes[uid2] += 1

            if not no_data:
                tss = [self.characteristics[c_uuid].records[best_indexes[c_uuid]][0] for c_uuid in self.keys]
                tss = [sum(tss)/len(tss)]
                for c_uuid in self.keys:
                    tss = tss + list(self.characteristics[c_uuid].records[best_indexes[c_uuid]][1:])

                for inum, c_uuid in enumerate(self.keys):
                    self.characteristics[c_uuid].records = self.characteristics[c_uuid].records[best_indexes[c_uuid]+1:]
                
                global ctr, limit
                if ctr > limit:
                    raise StopIteration
                t, a_x, a_y, a_z, w_x, w_y, w_z = tss
                if a_x != w_x:
                    ctr += 1

                    lines.append(f"{t} {a_x} {a_y} {a_z} {w_x} {w_y} {w_z}\n")


    def stream_data_in_buffer(self, cHandle, data):
        logging.info('received. handle=%s, len=%s', cHandle, len(data))
        logging.debug('%s', to_hex(data))
        for c_uuid, char in self.characteristics.items():
            if char.handle == cHandle:
                char.on_data(data)
                self.sync_characteristics()
                return
        logging.warning("Data from unknown characteristics. Ignored")

    def _show_all_services_and_characteristics(self):
        for s in self.device.getServices():
            logging.debug(f"SERVICE {s.uuid}")
            for c in s.getCharacteristics():
                logging.debug(f"    CHARACTERISTIC {c.uuid} HANDLE {c.valHandle}")

    def _connect_to_device(self, mac_addr, addrType=btle.ADDR_TYPE_RANDOM):

        class MyDelegate(btle.DefaultDelegate):
            _callback = None

            def __init__(self, callback):
                self._callback = callback
                btle.DefaultDelegate.__init__(self)

            def handleNotification(self, cHandle, data):
                self._callback(cHandle, data)

        self.device = btle.Peripheral(mac_addr, addrType)
        self.device.setMTU(2048)
        self.device.setDelegate(MyDelegate(self.stream_data_in_buffer))


    def subscribe_to_characteristics(self):
        for c_uuid, char in self.characteristics.items():
            c_acc = self.device.getCharacteristics(uuid=c_uuid)
            c_acc_handle = c_acc[0].getHandle()
            char.handle = c_acc_handle
            self.device.writeCharacteristic(c_acc_handle + 1, b'\x01\x00', withResponse=True)

    def disconnect(self):
        self.device.disconnect()

    def connect(self, addrType=btle.ADDR_TYPE_RANDOM):
        logging.info("Connecting to %s", self.device_addr)
        self._connect_to_device(self.device_addr, addrType=addrType)
        return self


if __name__ == '__main__':
    logging_levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']

    parser = argparse.ArgumentParser(description='StarGate blue tooth log reader')
    parser.add_argument('--loglevel', choices=logging_levels,
                        default='INFO', type=str,
                        help='application (not blue tooth device) log level')


    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--device', type=str, help='device alias')
    group.add_argument('--address', type=str, help='device address')

    cmd_args = parser.parse_args()
    loglevel = getattr(logging, cmd_args.loglevel.upper())
    logging.basicConfig(level=loglevel)

    tracker = ActivityTracker(
        device_addr=cmd_args.address or ActivityTracker._discover_address_by_name(cmd_args.device),
    )

    tracker.connect()
    if loglevel == 'DEBUG':
        tracker._show_all_services_and_characteristics()
    tracker._show_all_services_and_characteristics()
    tracker.subscribe_to_characteristics()
    print("Start!")
    while True:
        try:
            if tracker.device.waitForNotifications(1.0):
                continue
            logging.info(".")
        except KeyboardInterrupt:
            logging.info("Done")
            break
        except Exception as e:
            logging.exception(e)
            break
    tracker.disconnect()
    with open("data.txt", encoding="utf-8", mode="w") as f:
        f.writelines(lines)
    process("data.txt")
