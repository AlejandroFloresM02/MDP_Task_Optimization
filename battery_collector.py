import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.utils import uri_helper

# URI to the Crazyflie to connect to
drone_id = "80"
uri = uri_helper.uri_from_env(default='radio://0/'+ drone_id + '/2M/E7E7E7E7E7')
v_drop = 0.56

def voltage_callback(timestamp, data, logconf):
    bat = data["pm.vbat"]-v_drop
    print(bat, bat + v_drop)
    try:
        with open("temp/last_v"+drone_id+".txt", "w") as file:
            file.write(str(bat))
    except:
        print("Busy")

def start_voltage_printing(scf):
    log_conf = LogConfig(name='Voltage', period_in_ms=100)
    log_conf.add_variable("pm.vbat", "float")
    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(voltage_callback)
    log_conf.start() 


action_dur = 4 #minutes
time_limit = 35
def recharge_seq(scf):
    cf = scf.cf

    for timer in range(0,time_limit,action_dur):
        if timer == 0:
            ended = False
            while not ended:
                try:
                    with open("temp/last_v"+drone_id+".txt","r") as file:
                        voltage = float(file.readline())
                    with open("data/recharge"+drone_id+".txt", "a") as file:
                        file.write(str(voltage) + " ")
                        ended = True
                except:
                    continue
        elif timer >= time_limit - action_dur:
            ended = False
            while not ended:
                try:
                    with open("temp/last_v"+drone_id+".txt","r") as file:
                        voltage = float(file.readline())
                    with open("data/recharge" + drone_id + ".txt", "a") as file:
                        file.write(str(voltage) + "\n")
                        ended = True
                except:
                    continue
        else:
            ended = False
            while not ended:
                try:
                    with open("temp/last_v"+drone_id+".txt","r") as file:
                        voltage = float(file.readline())
                    with open("data/recharge" + drone_id + ".txt", "a") as file:
                        file.write(str(voltage) + "\n" + str(voltage) + " ")
                        ended = True
                except:
                    continue
        time.sleep(action_dur*60)

    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing


if __name__ == '__main__':
    print("Loading drivers")
    cflib.crtp.init_drivers(enable_debug_driver=False)
    print("Drivers loaded")
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        start_voltage_printing(scf)
        print("Running sequence")
        with open("data/recharge" + drone_id + ".txt", "a") as file:
            file.write("\n")
        recharge_seq(scf)