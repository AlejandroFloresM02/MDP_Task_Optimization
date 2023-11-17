# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2016 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
"""
Simple example that connects to one crazyflie (check the address at the top
and update it to your crazyflie address) and send a sequence of setpoints,
one every second.

This example is intended to work with the Loco Positioning System in TWR TOA
mode. It aims at documenting how to set the Crazyflie in position control mode
and how to send setpoints.
"""
import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.utils import uri_helper

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/100/2M/E7E7E7E7E7')
path_name = "path_1"

# Change the sequence according to your setup
#             x    y    z  YAW
sequence = eval("actions/"+ path_name + ".txt")


def wait_for_position_estimator(scf):
    print('Waiting for estimator to find position...')

    log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
    log_config.add_variable('kalman.varPX', 'float')
    log_config.add_variable('kalman.varPY', 'float')
    log_config.add_variable('kalman.varPZ', 'float')

    var_y_history = [1000] * 10
    var_x_history = [1000] * 10
    var_z_history = [1000] * 10

    threshold = 0.001

    with SyncLogger(scf, log_config) as logger:
        for log_entry in logger:
            data = log_entry[1]

            var_x_history.append(data['kalman.varPX'])
            var_x_history.pop(0)
            var_y_history.append(data['kalman.varPY'])
            var_y_history.pop(0)
            var_z_history.append(data['kalman.varPZ'])
            var_z_history.pop(0)

            min_x = min(var_x_history)
            max_x = max(var_x_history)
            min_y = min(var_y_history)
            max_y = max(var_y_history)
            min_z = min(var_z_history)
            max_z = max(var_z_history)

            # print("{} {} {}".
            #       format(max_x - min_x, max_y - min_y, max_z - min_z))

            if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                break


def reset_estimator(scf):
    cf = scf.cf
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')

    wait_for_position_estimator(cf)


def position_callback(timestamp, data, logconf):
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']
    bat = data["pm.vbat"]
    print('pos: ({}, {}, {}, {})'.format(x, y, z, bat))
    try:
        with open("temp/last_v.txt", "w") as file:
            file.write(str(bat))
    except:
        print("Busy")

def start_position_printing(scf):
    log_conf = LogConfig(name='Position', period_in_ms=100)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')
    log_conf.add_variable("pm.vbat", "float")

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start() 


def run_sequence(scf, sequence):
    cf = scf.cf

    for position in range(len(sequence)):
        print('Setting position {}'.format(sequence[position]))
        if position == 3:
            ended = False
            while not ended:
                try:
                    with open("temp/last_v.txt","r") as file:
                        voltage = float(file.readline())
                    with open("data/"+path_name + ".txt", "a") as file:
                        file.write(str(voltage))
                        ended = True
                except:
                    continue
        if position == len(sequence)-2:
            ended = False
            while not ended:
                try:
                    with open("temp/last_v.txt","r") as file:
                        voltage = float(file.readline())
                    with open("data/"+path_name + ".txt", "a") as file:
                        file.write(" " + str(voltage) + "\n")
                        ended = True
                except:
                    continue
        for i in range(13):
            cf.commander.send_position_setpoint(sequence[position][0],
                                                sequence[position][1],
                                                sequence[position][2],
                                                sequence[position][3])
            time.sleep(0.1)
            

    cf.commander.send_stop_setpoint()
    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.1)


if __name__ == '__main__':
    print("Loading drivers")
    cflib.crtp.init_drivers(enable_debug_driver=False)
    print("Drivers loaded")
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        print("Resetting estimator")
        reset_estimator(scf)
        start_position_printing(scf)
        print("Running sequence")
        with open("data/"+path_name + ".txt", "a") as file:
            file.write("\n")
        while True:
            run_sequence(scf, sequence)
            for i in range(0,20):
                scf.cf.commander.send_position_setpoint(2,1,1.5,0)
                time.sleep(0.1)
            for i in range(0,20):
                scf.cf.commander.send_position_setpoint(0.5,0.5,1.5,0)
                time.sleep(0.1)